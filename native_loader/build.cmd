@echo off
setlocal
if defined VCINSTALLDIR goto compiler_ready
if exist "%ProgramFiles(x86)%\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" (
 call "%ProgramFiles(x86)%\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
 if errorlevel 1 exit /b 1
) else (
 echo Run this script from an x64 Native Tools Command Prompt for Visual Studio 2022.
 exit /b 1
)
:compiler_ready
cd /d "%~dp0"
if not exist build mkdir build
set "MH=%~dp0..\third_party\minhook"
cl /nologo /O2 /MT /c /I"%MH%\include" dinput8_proxy.cpp /Fobuild\dinput8_proxy.obj
if errorlevel 1 exit /b 1
cl /nologo /O2 /MT /TC /c /I"%MH%\include" "%MH%\src\buffer.c" "%MH%\src\hook.c" "%MH%\src\trampoline.c" "%MH%\src\hde\hde64.c" /Fobuild\
if errorlevel 1 exit /b 1
link /nologo /DLL /MACHINE:X64 /DEF:dinput8.def /OUT:build\dinput8.dll build\dinput8_proxy.obj build\buffer.obj build\hook.obj build\trampoline.obj build\hde64.obj kernel32.lib user32.lib
exit /b %errorlevel%
