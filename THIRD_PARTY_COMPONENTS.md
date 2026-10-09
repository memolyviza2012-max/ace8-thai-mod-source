# Third-party provenance

- MinHook: https://github.com/TsudaKageyu/minhook
  Local clean source commit: `d94c64d32ea37bc4f5ee47d580709f70c6fb6080`. Exact include/src snapshot and BSD license are included.
- Shipped `dwmapi.dll` and `UE4SS/UE4SS.dll`: obtained from the tested AC8HOTAS v0.1.0 full-install distribution:
  https://github.com/Drumsmasher17/AC8HOTAS/releases/tag/v0.1.0
  Upstream loader source: https://github.com/UE4SS-RE/RE-UE4SS
  They are third-party binaries; this review bundle does not claim to reproduce them from our own code.
  Their precise shipped SHA256 values are in RELEASE_HASHES.json. A separate exact UE4SS source commit is not established in our records; the AC8HOTAS distribution is the pinned provenance.
  UE4SS MIT license is included. No AC8HOTAS controller Lua mod or analog-yaw DLL is shipped in this Thai mod.
- Prompt font: https://github.com/google/fonts/tree/main/ofl/prompt (SIL OFL license included).

This source-review ZIP contains no compiled executable/DLL, game binaries, original proprietary font assets, nested archives or account/save files.
