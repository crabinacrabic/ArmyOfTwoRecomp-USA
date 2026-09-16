<div align="center">
  <img src="assets/icon.png" alt="ArmyOfTwoRecomp" width="480" align="right">
</div>

# Army Of Two XBOX360 Recompilation

A static recompilation of [**Army of Two**](https://en.wikipedia.org/wiki/Army_of_Two) (2006, Volition Games, Xbox 360;
Title ID `4541084C`, retail hash `AA1EA03FEC9A549C`) to native Windows x86-64,
built on the [ReXGlue SDK](https://github.com/rexglue/rexglue-sdk).

Static recompilation translates the Xbox 360 PowerPC code inside the game's
`default.xex` into native C++ that compiles and runs on a PC. There is no
emulator and no interpreter in the loop; file I/O, GPU commands, audio and
threading go through the ReXGlue runtime.


## Status

Everything works smoothly - codegen runs clean, the build compiles, and the
executable boots to real GPU rendering.

## Requirements

- CMake 3.25+
- Ninja
- Clang / LLVM
- [ABGX360](https://github.com/BakasuraRCE/abgx360) to dump the Xbox 360 disc,
  or [extract-xiso](https://github.com/XboxDev/extract-xiso/releases) to
  unpack an existing ISO
- Your own legally-owned copy of Army of Two, extracted from the Xbox 360 disc/ISO

The ReXGlue SDK release archive is auto-downloaded by the CMake configure
step - see [Getting the SDK](#getting-the-sdk).

## Getting the SDK

The ReXGlue SDK version is pinned in [`CMakeLists.txt`](CMakeLists.txt)
(`REXSDK_VERSION "0.10.0.8-dev.g1406e1b"`). The CMake configure step
auto-downloads the matching nightly release archive for your platform
(Windows / Linux / macOS) into `rexglue/<platform>/` via
[`cmake/fetch-rexglue-sdk.cmake`](cmake/fetch-rexglue-sdk.cmake) - no manual
download needed. The SDK itself is gitignored; only
[`rexglue/README.md`](rexglue/README.md) is checked in.

## Getting the game data

1. Dump the Xbox 360 disc with
   [ABGX360](https://github.com/BakasuraRCE/abgx360) (verify against the
   hashes below) or extract an existing ISO with
   [extract-xiso](https://github.com/XboxDev/extract-xiso/releases), which
   unpacks the disc's file tree.
2. Copy the extracted contents directly into `assets/`, so `default.xex`
   sits at `assets/default.xex` alongside the rest of the disc's files
   (`AO2Game/`, `$SystemUpdate/`, ...).
3. `assets/` is gitignored (`assets/*` in `.gitignore`, with a couple of
   small tracked exceptions) - nothing from the disc is, or should be,
   committed to this repo.

Target retail release (verify your dump matches):

| Field | Value |
|---|---|
| Title ID | `4541084C` |
| Module Hash | `AA1EA03FEC9A549C` |
| Media ID | `7E3E9BEA` |

## Build

```powershell
cmake --preset win-amd64-release
cmake --build --preset win-amd64-release
```

```bash
cmake --preset linux-amd64-release
cmake --build --preset linux-amd64-release
```

```bash
cmake --preset mac-amd64-release
cmake --build --preset mac-amd64-release
```

Other presets (`*-debug`, `*-relwithdebinfo`, `*-arm64`) are listed in
[`CMakePresets.json`](CMakePresets.json).

Codegen (translating `assets/default.xex` into `generated/default/*.cpp`) runs
automatically as a build step (`armyoftworecomp_codegen` CMake target)
whenever `armyoftworecomp_manifest.toml` or an included `.toml`
changes. It can also be run directly: `rexglue\win-amd64\bin\rexglue.exe
codegen`.

## Run

```powershell
cd out\build\win-amd64-release
.\armyoftworecomp.exe
```

```bash
cd out/build/linux-amd64-release
./armyoftworecomp
```

```bash
cd out/build/mac-amd64-release
./armyoftworecomp
```

Both `--game_data_root` and `--gpu_plugin` are optional: `OnConfigurePaths()`
in [`src/armyoftworecomp_app.h`](src/armyoftworecomp_app.h)
defaults `game_data_root` to `<repo_root>/assets` when it isn't set via
flag/env var, and `gpu_plugin = "xenos"` already lives in
[`settings/hardware.toml`](settings/hardware.toml).

Useful extra flags/env vars while developing:

| Flag / env var | Effect |
|---|---|
| `--game_data_root <path>` | Overrides the default `<repo_root>/assets` game-files location. |
| `--gpu_plugin xenos` | Overrides `settings/hardware.toml`'s `gpu_plugin`. Only needed if you want a different plugin than the file specifies. |
| `--graphics_backend d3d12\|vulkan\|any` | Forces the graphics API `rexgpu-xenos` uses (cvar, default `"any"`, which picks D3D12 first). See [`settings/README.md`](settings/README.md). |
| `--ao2_fps_unlock=true` | Ported xenia-canary `game-patches` "Unlock FPS" patch for Army of Two retail. Enabled by default in [`settings/hardware.toml`](settings/hardware.toml). See [`settings/README.md`](settings/README.md). |
| `--ao2_fps_unlock_mode=0\|1\|2` | Frame-rate target when `ao2_fps_unlock` is on: `0`=unlimited, `1`=60 FPS, `2`=30 FPS. Default `1`. |
| `--ao2_disable_msaa=true` | Ported xenia-canary `game-patches` "Black Shading Fix" (disables MSAA). Enabled by default in [`settings/hardware.toml`](settings/hardware.toml). |
| `--ao2_anisotropic_16x=true` | Ported xenia-canary `game-patches` "16x Anisotropic Filtering". Off by default. |

Logs are written to `out\build\<preset>\logs\*.log` (the exe is built `WIN32`,
so nothing prints to the console).

## Configuration

Rendering/window/vsync and input-backend defaults are checked in under
[`settings/`](settings/README.md) (`hardware.toml` / `mapping.toml`), loaded
automatically at startup. CLI flags and `REX_*` environment variables always
override them - see [`settings/README.md`](settings/README.md) for the full
reference and precedence rules.

## Credits

- [ReXGlue SDK](https://github.com/rexglue/rexglue-sdk) ([releases](https://github.com/rexglue/rexglue-sdk/releases))
- [ABGX360](https://github.com/BakasuraRCE/abgx360) - used to dump the Xbox 360 disc
- [extract-xiso](https://github.com/XboxDev/extract-xiso) ([releases](https://github.com/XboxDev/extract-xiso/releases)) -
  used to unpack the Xbox 360 ISO into the file tree copied into `assets/`
- [xenia](https://github.com/xenia-project/xenia) / [xenia-canary](https://github.com/xenia-canary/xenia-canary) -
  ReXGlue's runtime is derived from Xenia's
- [xenia-canary/game-patches](https://github.com/xenia-canary/game-patches) -
  source of the ported `ao2_fps_unlock` / `ao2_disable_msaa` /
  `ao2_anisotropic_16x` patches
- [mdqinc/SDL_GameControllerDB](https://github.com/mdqinc/SDL_GameControllerDB) -
  `settings/gamecontrollerdb.txt`
