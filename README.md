# ACE COMBAT 8 Thai Mod — source for Nexus safety review

Author: NodNuatTranslator (หน๊ด หนวด translator). Source snapshot for mod **v2.3**.

Mod page: https://www.nexusmods.com/acecombat8wingsoftheve/mods/13?tab=files

This repository publishes the complete custom C# launcher and C++ DirectInput
proxy, pinned MinHook sources, shipped Lua/configuration, build instructions and
release hashes. It is a source review repository; it does not distribute game
binaries, translation archives, saves, compiled DLLs, or account credentials.

## Build and review

- [Build instructions and behavior](README_REVIEW.md)
- Launcher: `launcher/ACE8ThaiPortableLauncher.cs`; run `launcher/build.cmd` on
  Windows with .NET Framework 4.x (64-bit C# compiler).
- Native DLL: `native_loader/dinput8_proxy.cpp` and `dinput8.def`; run
  `native_loader/build.cmd` with Visual Studio 2022 C++ Build Tools and Windows SDK.
  MinHook is included at commit `d94c64d32ea37bc4f5ee47d580709f70c6fb6080`.
- Outputs remain in each component's `build/` directory and are excluded from Git.
- [Third-party provenance](THIRD_PARTY_COMPONENTS.md): UE4SS binaries originate
  from AC8HOTAS v0.1.0. Their exact UE4SS source commit is not established; this
  repository does not claim to rebuild those third-party binaries.
- [Shipped file SHA256](RELEASE_HASHES.json), [current build check](PUBLIC_BUILD_VERIFICATION.json),
  and [review email draft](NEXUS_SUPPORT_DRAFT.txt).

The native DLL makes guarded in-process container signature/reader changes for
the exact authored Thai PAK/TOC. The launcher selects the game's offline Null
Client configuration. This is disclosed in README_REVIEW.md; it is not a claim
of protected online compatibility. Neither component changes Windows Defender
settings. A compilation pass or publication on GitHub is not a malware verdict
or Nexus approval.

The author reported project completion on 2026-10-08. Historical pending-test
notes are retained in the original review documentation. The exact scan trigger
and the result of Nexus review remain unknown.

`font_generation/` provides the font generation source for inspection. Its local
project paths and input asset requirements are documented; it is not a standalone
asset reproduction kit. No proprietary source font/game data or research key is
published. The custom launcher/native code is preserved byte-for-byte from the
previous source-review ZIP, rather than edited into a different implementation.

## Rights

Third-party components retain the licenses included under `licenses/` and
`third_party/minhook/`. Custom source is published for inspection; no new blanket
open-source license is asserted by this snapshot.
