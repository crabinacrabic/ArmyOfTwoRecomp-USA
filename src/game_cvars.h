// game_cvars.h - Game-specific CVAR declarations
#pragma once

#include <cstdint>

#include <rex/cvar.h>

REXCVAR_DECLARE(std::string, graphics_backend);
REXCVAR_DECLARE(bool, ao2_fps_unlock);
REXCVAR_DECLARE(int32_t, ao2_fps_unlock_mode);
REXCVAR_DECLARE(bool, ao2_disable_msaa);
REXCVAR_DECLARE(bool, ao2_anisotropic_16x);
REXCVAR_DECLARE(bool, dev_debug_runtime);
