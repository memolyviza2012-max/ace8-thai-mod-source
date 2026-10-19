# ACE8 Thai Setup 2.4

This is the exact C# source used for the packaged installer. Windows x64,
.NET Framework 4.x C# compiler, WinForms/System.Drawing/System.Web.Extensions.
It follows the author's Modern Warfare 2019 branded setup UI, adapted to
ACE8 Steam discovery and the game's own verified payload. It is **full-file**,
not a binary-delta patcher: all 18 mod files are additions, so there is no
original game-file baseline to delta against. The unchanged original EXE,
bootstrap and Settings are only verified by SHA256, not redistributed.

## Rebuild

Download the matching official 2.4 installer and check its SHA256 against
INSTALLER_2_4_HASHES.json at the repository root. From this directory run:

```bat
ACE8ThaiSetup_v2.4.exe --export-resources Resources
BUILD.cmd
```

Export mode only writes the four named resources to a new chosen directory;
it does not install, run a payload, start a game, contact a network endpoint,
or change security settings. Existing files are not overwritten by export.
Resources are the manifest, gzip-compressed length-prefixed payload, header
image and icon. Resource SHA256 values are pinned in Engine.cs. The binary
resource format is parsed explicitly and all member hashes are checked.
No encrypted/obfuscated archive, password, UPX or runtime download is used.
Compilation/PE timestamps may prevent byte-identical rebuilds; no reproducible
binary claim is made. All runtime native sources remain at launcher/ and
native_loader/ in the root, third-party provenance remains documented there.

## Installation behavior

- Auto-discovery reads Steam registry and libraryfolders/appmanifest files;
  manual Browse and explicit multiple-root selection are available. It does
  not recursively scan disks. The full original executable/launcher/Settings
  hashes must match the tested Steam build 25201480 before changing files.
- All 18 relative destinations are embedded in manifest.json. Unknown existing
  DLLs/files, other UE4SS mod folders, reparse paths, read-only targets, an active
  game, or insufficient space are rejected. No elevation is requested by default.
- It snapshots each current authored target state and original Settings before
  writes, verifies backup bytes, marks backups read-only, persists a pending
  record and flushes a checkpoint log. Backups live in ACE8Thai_Setup_Data under
  the selected game directory and are retained after uninstall.
- Replacement data is staged under that owned data directory, flushed and
  atomically moved/replaced on the same volume. A pending transaction is verified
  and rolled back before retry. Corrupt backups or unexpected outside changes
  stop recovery rather than forcing writes. No arbitrary manifest commands run.
- Existing recognized copy-over mod versions can be upgraded. Their files are
  backed up for transaction rollback. Uninstall removes known mod additions;
  it does not reinstall the previous mod version. Original game EXE, bootstrap,
  Settings, saves and unrelated files are never replaced/deleted.
- No firewall/Defender modification, automatic game launch, online blocking rule,
  scheduled task or network call is created by the installer. The payload still
  contains the existing offline Null Client launcher and guarded in-process
  container hooks; those runtime behaviors are described in README_REVIEW.md.

TEST_RESULTS.json records actual packaged-EXE disposable-fixture tests, including
process termination mid-install. A harmless named sleeper tests the running-game
guard; the real game was never started. Insufficient-space logic and hostile
relative paths are self-tested; a physically full disk was not created. No new
full game mission/performance test is implied. The author explicitly accepted
the HUD correction on 2026-10-19. New wording changes were packed afterward.
Nexus approval or a malware verdict is not asserted.
