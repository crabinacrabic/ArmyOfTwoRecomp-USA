# AGENTS.md - instructions for AI agents

Army of Two (2008), Xbox 360, **USA disc (Title ID `454107F8`)**, statically
recompiled with ReXGlue SDK `0.10.0.8-dev.g1406e1b`. The maintainer speaks
Russian; code, comments and commit messages are in English.

## Where this project comes from

`main` is [nikolaygorb/ArmyOfTwoRecomp](https://github.com/nikolaygorb/ArmyOfTwoRecomp)
(Europe, `4541084C`; boots with no guest overrides) retargeted to the USA disc.
The EU and USA `default.xex` have the same functions at the same addresses
(`.pdata` identical, entry `0x82A3C128`) but a different `.rdata` layout: about
55 700 instructions hold different data addresses, so a build is tied to one
XEX. Codegen on the USA XEX with the same `default_functions.toml` is the port.

The earlier attempt (SDK 0.8 and 0.10 with ~100 hand patches, edits inside
`generated/`) is kept in the branches `legacy-v0.8-hacks`, `clean-v0.10`,
`feat/cpu-idle-timing-hooks` (last snapshot `e73ca24`) and on the `legacy`
remote. Do not port its patches blindly: most worked around problems this
clean base does not have.

## Rules

1. Do not run builds or code generation from the terminal (`cmake --build`,
   `ninja`, `rexglue codegen`, compilers) unless the user asks. The user
   builds in Visual Studio (`F7` / `F5`). Launching the built exe is fine.
2. `generated/` is written by codegen and is read-only. Fix guest code through
   `src/` (strong symbols / `REX_HOOK`) or `default_functions.toml`.
3. Never commit game files (`assets/` except `README.md` and `icon.png`).
4. Push only when the user asks.

## Build and run

- Game files: the USA disc unpacked into `assets/` (`assets/default.xex`,
  `assets/AO2Game/`), `default.xex` SHA-1 `0228895185EB2F1750C4B729F6CB73C36E82816A`.
- Visual Studio 2026: **File -> Open -> Folder** (the repository root, not a
  `.sln`), preset **`local-win-relwithdebinfo`**, `F7`. The first configure
  runs codegen once (`generated/default/`), the first build compiles it.
- Exe: `out\build\local-win-relwithdebinfo\armyoftworecomp.exe`; settings
  `settings\hardware.toml`, `settings\mapping.toml`; logs
  `out\build\<preset>\logs\`.

## Map

```
armyoftworecomp_manifest.toml   codegen manifest (includes default_functions.toml)
default_functions.toml          extra function entries found by stub sweeps
src/armyoftworecomp_app.h       ReXApp: paths (<repo>/assets), settings files
src/game_patches.h, game_constants.h   xenia-canary patches (FPS unlock, MSAA, AF); addresses valid for EU and USA
src/debug_tools.h               stub sweep / missed-function scan (dev_debug_runtime)
settings/                       hardware.toml (SDK config), mapping.toml (input)
```
