# ACE COMBAT 8 Thai Mod v2.3 — manual-review source bundle

Author: NodNuatTranslator (หน๊ด หนวด translator)
Mod page: https://www.nexusmods.com/acecombat8wingsoftheve/mods/13?tab=files
Prepared new upload: ACE COMBAT 8 WINGS OF THEVE ThaiMod V2.3; quarantine/review status not yet verified
Released ZIP SHA256: `37b832a42f67e74133cf05afceaa0be339e86407ed626dd9ecea2b2d843e1aa7`

## Contents and build instructions

1. `launcher/ACE8ThaiPortableLauncher.cs` is the custom launcher source used for the shipped ACE8ThaiLauncher.exe.
   On Windows with .NET Framework 4.x compiler installed, run `launcher/build.cmd`.
   Output: launcher/build/ACE8ThaiLauncher.exe. The script uses the same x64 Windows EXE/reference flags as the release build.
2. `native_loader/dinput8_proxy.cpp` and `dinput8.def` are the full custom native-loader sources.
   Install Visual Studio 2022 C++ Build Tools with an appropriate Windows SDK.
   Run native_loader/build.cmd from an x64 Native Tools Command Prompt (or the standard VS2022 BuildTools location).
   Output: native_loader/build/dinput8.dll. Bundled MinHook sources are compiled directly using /O2 /MT; no dependency download is performed.
   Build scripts use relative dependency paths instead of the author's workstation paths; source logic and original compiler/linker flags are retained.
3. Diagnostic CMD/PowerShell scripts are not included in the v2.3 runtime distribution; no need to run them to install or play.
4. `runtime_configuration/` contains the shipped read-only Lua diagnostic and loader configuration.
5. `THIRD_PARTY_COMPONENTS.md` identifies third-party loader provenance and licenses.

## Behavior requiring transparent review

The launcher sets EOS_USE_ANTICHEATCLIENTNULL=1, SteamAppId/SteamGameId=2288340 and starts the game's existing start_protected_game.exe with
`-SaveToUserDir -anticheat_settings=ACE8Thai_Offline.json`. It writes a launch log beside itself.
The included offline settings enable the game's Null Client configuration. This package does not claim protected online compatibility.

The native DLL proxies five DirectInput exports to the absolute System32 dinput8.dll path.
It uses MinHook for in-process detours. It requires the exact offline environment, host executable, PE timestamp/image-size and byte guards before applying its authored-container logic.
For the exact authored pakchunk0-Windows_999_P container it selects the unsigned PAK reader and temporarily returns an empty signing delegate for the corresponding font TOC read on the calling thread.
This is a game-specific runtime signature-check modification for authored localization/font containers, not an on-disk edit of the original EXE or a Windows security-setting change.
Reviewers should inspect the full implementation and guards rather than treat this summary as a security certification.

The v2.3 runtime ZIP contains no diagnostic CMD/PowerShell. The UE4SS Lua probe inspects object names and writes a diagnostic log; its complete shipped source is included.

## Why review is requested

The v2.0 and v2.2 uploads were quarantined. The author confirmed v2.2 quarantine on 2026-10-04. The v2.3 scanner status is still unknown. The triggering file/check is not known; no confirmed false-positive or antivirus verdict is asserted.
Version 2.3 replaces the blurred Thai SDF atlas encoding with 8x supersampled alpha coverage and corrects padded glyph advances, while preserving the v2.2 translation. Font payload round-trip and raster coverage checks pass; the latest runtime rendering acceptance is pending.
The full package retains the existing launcher and all DLLs byte-for-byte. Optional diagnostic CMD/PowerShell files are omitted because they are not runtime dependencies.
This does not hide or rename executable payloads: all required runtime executables remain transparently listed with hashes.
A separate data-only UPDATE_FROM_v2.0 archive is intended exclusively for users who already have the functional v2.0 runtime; it is not a standalone installation or a replacement for required runtime review.
The new file has not been approved by Nexus at packaging time. Please review this exact release, including the custom guarded container signature handling and UE4SS third-party components.
There are no nested or password-protected archives in the release or source bundle. No Windows security settings are changed by packaging.

Build verification results are in BUILD_VERIFICATION.json. Compilation success is not a malware verdict or a guarantee of byte-identical output across compiler versions/timestamps.
No game is started and no compiled library is loaded during our review-bundle checks.
