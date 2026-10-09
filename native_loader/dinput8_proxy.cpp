#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <unknwn.h>
#include <cwchar>
#include <cstring>
#include <cstdio>
#include "MinHook.h"

// Build-specific, offline-only experiment. Never modifies executable on disk.
static HMODULE self_module;
static HMODULE real_module;
static INIT_ONCE real_once = INIT_ONCE_STATIC_INIT;
static SRWLOCK log_lock = SRWLOCK_INIT;
using PakCtor = void* (__fastcall*)(void*, void*, const wchar_t*, bool, bool);
static PakCtor original_ctor;
using TocRead = void* (__fastcall*)(void*,const wchar_t*,size_t,void*);
using SigningDelegate = void* (__fastcall*)();
static TocRead original_toc_read;
static SigningDelegate original_signing_delegate;
static thread_local bool reading_our_toc=false;
static __declspec(align(16)) unsigned char empty_delegate[16]={};
static void log_line(const char* message) {
    wchar_t path[MAX_PATH];
    if (!GetModuleFileNameW(self_module, path, MAX_PATH)) return;
    wchar_t* slash = wcsrchr(path, L'\\');
    if (!slash) return;
    wcscpy_s(slash + 1, MAX_PATH - (slash + 1 - path), L"ACE8Thai_PakProbe.log");
    AcquireSRWLockExclusive(&log_lock);
    HANDLE file = CreateFileW(path, FILE_APPEND_DATA, FILE_SHARE_READ | FILE_SHARE_WRITE,
        nullptr, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, nullptr);
    if (file != INVALID_HANDLE_VALUE) {
        SYSTEMTIME t; GetLocalTime(&t);
        char buffer[1024];
        int length = sprintf_s(buffer, "%04u-%02u-%02u %02u:%02u:%02u.%03u %s\r\n",
            t.wYear,t.wMonth,t.wDay,t.wHour,t.wMinute,t.wSecond,t.wMilliseconds,message);
        DWORD written; if (length > 0) WriteFile(file, buffer, length, &written, nullptr);
        CloseHandle(file);
    }
    ReleaseSRWLockExclusive(&log_lock);
}
static BOOL CALLBACK load_real(PINIT_ONCE, PVOID, PVOID*) {
    wchar_t path[MAX_PATH];
    UINT n = GetSystemDirectoryW(path, MAX_PATH);
    if (!n || n + 13 >= MAX_PATH) return FALSE;
    wcscat_s(path, L"\\dinput8.dll");
    real_module = LoadLibraryW(path);
    return real_module != nullptr;
}
static FARPROC resolve(const char* name) {
    if (!InitOnceExecuteOnce(&real_once, load_real, nullptr, nullptr)) return nullptr;
    return GetProcAddress(real_module, name);
}
static bool is_target(const wchar_t* path) {
    if (!path) return false;
    const wchar_t* base = path;
    for (const wchar_t* p=path; *p; ++p) if (*p==L'/' || *p==L'\\') base=p+1;
    return _wcsicmp(base,L"pakchunk0-Windows_999_P.pak")==0;
}
static bool is_target_toc(const wchar_t* path) {
    if (!path) return false;
    const wchar_t* base=path;
    for(const wchar_t* p=path;*p;++p)if(*p==L'/' || *p==L'\\')base=p+1;
    return _wcsicmp(base,L"pakchunk0-Windows_999_P.utoc")==0;
}
static void* __fastcall signing_delegate() {
    if(reading_our_toc)return empty_delegate;
    return original_signing_delegate();
}
static void* __fastcall read_toc(void* status,const wchar_t* path,size_t options,void* resource) {
    bool target=is_target_toc(path),previous=reading_our_toc;
    if(target){reading_our_toc=true;log_line("Font TOC reader reached; signing delegate unbound for this thread/call only");}
    void* result=original_toc_read(status,path,options,resource);
    reading_our_toc=previous;
    if(target){char line[256];sprintf_s(line,"Font TOC reader returned: status=%u (0 means success)",*(unsigned*)status);log_line(line);}
    return result;
}
static void* __fastcall construct_pak(void* object, void* platform,
    const wchar_t* path, bool signed_mode, bool load_index) {
    if (!is_target(path)) return original_ctor(object,platform,path,signed_mode,load_index);
    log_line("POC2 constructor reached; selecting unsigned reader only for this PAK");
    void* result = original_ctor(object,platform,path,false,load_index);
    char line[256];
    sprintf_s(line,"POC2 constructor returned: previous_signed=%u load_index=%u valid=%u resulting_signed=%u",
        unsigned(signed_mode),unsigned(load_index),unsigned(((unsigned char*)object)[0x211]),
        unsigned(((unsigned char*)object)[0x210]));
    log_line(line);
    return result;
}
static DWORD WINAPI install_probe(void*) {
    log_line("Proxy loaded; begin guarded offline PAK experiment");
    wchar_t env[8]={};
    if (GetEnvironmentVariableW(L"EOS_USE_ANTICHEATCLIENTNULL",env,8)!=1 || wcscmp(env,L"1")) {
        log_line("No exact Null Client environment; hook disabled"); return 0;
    }
    wchar_t exe[MAX_PATH]; GetModuleFileNameW(nullptr,exe,MAX_PATH);
    const wchar_t* name=wcsrchr(exe,L'\\');
    if (!name || _wcsicmp(name+1,L"AceCombat8.exe")) {
        log_line("Unexpected host; hook disabled"); return 0;
    }
    const wchar_t* command=GetCommandLineW();
    if (wcsstr(command,L"-signed") || wcsstr(command,L"-Signed")) {
        log_line("Explicit signed command line; experiment disabled"); return 0;
    }
    auto base=(unsigned char*)GetModuleHandleW(nullptr);
    auto dos=(IMAGE_DOS_HEADER*)base;
    auto nt=(IMAGE_NT_HEADERS64*)(base+dos->e_lfanew);
    if (nt->FileHeader.TimeDateStamp!=0x6aa0e27d || nt->OptionalHeader.SizeOfImage!=0x2195a000) {
        log_line("Executable version differs; hook disabled"); return 0;
    }
    const unsigned char guard[]={0x48,0x89,0x5c,0x24,0x10,0x48,0x89,0x6c,0x24,0x18,
        0x48,0x89,0x74,0x24,0x20,0x57,0x41,0x54,0x41,0x55,0x41,0x56,0x41,0x57,
        0x48,0x83,0xec,0x30,0x48,0x8d,0x05,0xe5,0x7a,0xf1,0x08,0x4c,0x8b,0xea,
        0x48,0x89,0x01,0x4c,0x8b,0xf1,0x48,0x8d,0x05,0x65,0x7a,0xf1,0x08,
        0x33,0xff,0x48,0x89,0x41,0x10,0x49,0x8b,0xd0,0x89,0x79,0x08,0x41};
    const unsigned char store[]={0x41,0x88,0xb6,0x10,0x02,0x00,0x00};
    if (memcmp(base+0x27f6c80,guard,sizeof(guard)) || memcmp(base+0x27f6e8e,store,sizeof(store))) {
        log_line("Constructor code guard differs; hook disabled"); return 0;
    }
    MH_STATUS status=MH_Initialize();
    if (status!=MH_OK) { log_line("MinHook initialization failed; hook disabled"); return 0; }
    void* target=base+0x27f6c80;
    status=MH_CreateHook(target,(void*)&construct_pak,(void**)&original_ctor);
    if (status==MH_OK) status=MH_EnableHook(target);
    char line[160]; sprintf_s(line,"Constructor hook installation status=%d (0 means success)",int(status));
    log_line(line);
    const unsigned char read_guard[]={0x40,0x55,0x53,0x57,0x41,0x54,0x41,0x57,0x48,0x8d,0xac,0x24,0xf0,0xfe,0xff,0xff,0x48,0x81,0xec,0x10,0x02,0x00,0x00,0x48,0x8b,0x05,0x32,0x69,0x49,0x0c,0x48,0x33};
    const unsigned char delegate_guard[]={0x48,0x83,0xec,0x28,0x65,0x48,0x8b,0x04,0x25,0x58,0x00,0x00,0x00,0xb9,0x4c,0x01,0x00,0x00,0x48,0x8b,0x00,0x8b,0x04,0x01,0x39,0x05,0x32,0xee,0xd5,0x0c,0x7f,0x0c};
    if(memcmp(base+0x17962b0,read_guard,sizeof(read_guard)) || memcmp(base+0x17f70e0,delegate_guard,sizeof(delegate_guard))) {
        log_line("TOC/delegate code guard differs; font hook disabled");return 0;
    }
    void* delegate_target=base+0x17f70e0;
    status=MH_CreateHook(delegate_target,(void*)&signing_delegate,(void**)&original_signing_delegate);
    if(status==MH_OK)status=MH_EnableHook(delegate_target);
    if(status!=MH_OK){log_line("Delegate hook failed; font hook disabled");return 0;}
    void* toc_target=base+0x17962b0;
    status=MH_CreateHook(toc_target,(void*)&read_toc,(void**)&original_toc_read);
    if(status==MH_OK)status=MH_EnableHook(toc_target);
    sprintf_s(line,"Selective Font TOC hook installation status=%d (0 means success)",int(status));log_line(line);
    return 0;
}
extern "C" HRESULT WINAPI DirectInput8Create(HINSTANCE instance,DWORD version,REFIID iid,LPVOID* out,LPUNKNOWN outer) {
    using Fn=HRESULT(WINAPI*)(HINSTANCE,DWORD,REFIID,LPVOID*,LPUNKNOWN);
    auto fn=(Fn)resolve("DirectInput8Create");return fn?fn(instance,version,iid,out,outer):E_FAIL;
}
extern "C" HRESULT WINAPI DllCanUnloadNow() {
    using Fn=HRESULT(WINAPI*)();auto fn=(Fn)resolve("DllCanUnloadNow");return fn?fn():S_FALSE;
}
extern "C" HRESULT WINAPI DllGetClassObject(REFCLSID cls,REFIID iid,LPVOID* out) {
    using Fn=HRESULT(WINAPI*)(REFCLSID,REFIID,LPVOID*);auto fn=(Fn)resolve("DllGetClassObject");return fn?fn(cls,iid,out):E_FAIL;
}
extern "C" HRESULT WINAPI DllRegisterServer() {
    using Fn=HRESULT(WINAPI*)();auto fn=(Fn)resolve("DllRegisterServer");return fn?fn():E_FAIL;
}
extern "C" HRESULT WINAPI DllUnregisterServer() {
    using Fn=HRESULT(WINAPI*)();auto fn=(Fn)resolve("DllUnregisterServer");return fn?fn():E_FAIL;
}
BOOL WINAPI DllMain(HINSTANCE module,DWORD reason,LPVOID) {
    if(reason==DLL_PROCESS_ATTACH) {
        self_module=module;DisableThreadLibraryCalls(module);
        HANDLE thread=CreateThread(nullptr,0,install_probe,nullptr,0,nullptr);
        if(thread)CloseHandle(thread);
    }
    return TRUE;
}
