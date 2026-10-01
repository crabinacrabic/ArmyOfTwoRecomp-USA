// game_patches.h - Game-specific memory patches
#pragma once

namespace game_patches
{
  enum class PatchId
  {
    FpsUnlock,
    DisableMsaa,
    AnisotropicFiltering16x
  };

  bool IsEnabled(PatchId patch);
  void ApplyEnabledPatches();
} // namespace game_patches
