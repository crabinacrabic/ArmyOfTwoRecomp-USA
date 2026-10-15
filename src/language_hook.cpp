// language_hook.cpp - keeps user_language within the languages on the disc.
//
// sub_82A399B0 is the statically linked XDK XGetLanguage(): it reads
// ExGetXConfigSetting(XCONFIG_USER_CATEGORY, XCONFIG_USER_LANGUAGE), which the
// SDK answers with the user_language cvar, and falls back to a region default
// for 0 or anything above 12. Unlike PDZ, the game never calls the SDK's own
// XGetLanguage export (that one ignores the cvar), so user_language in
// hardware.toml reaches the game without any hook.
//
// UE3's appGetLanguageExt (sub_8221F060) turns the ID into the INT/JPN/DEU/...
// suffix used for Localization/Coalesced.* and the *_LOC_* packages. The disc
// only ships 1..6 (int, jpn, deu, fra, esn, ita); anything else would send the
// engine after files that don't exist, so it is forced back to English here.
// Every caller (UE3 localization, speech recognition, font selection) goes
// through this function, so they all agree on the result.
//
// sub_82A399B0 overrides the weak recompiled symbol; __imp__sub_82A399B0 is the
// untouched original.

#include <rex/cvar.h>
#include <rex/hook.h>

#include "armyoftworecomp_pch.h"

namespace
{
  // XLanguage IDs with a Coalesced.* file on the disc: 1 English .. 6 Italian.
  constexpr uint32_t kLanguageEnglish = 1;
  constexpr uint32_t kLanguageMaxOnDisc = 6;
}

REX_EXTERN(__imp__sub_82A399B0);

REX_HOOK_RAW(sub_82A399B0)
{
  __imp__sub_82A399B0(ctx, base);
  if (ctx.r3.u32 < kLanguageEnglish || ctx.r3.u32 > kLanguageMaxOnDisc)
  {
    ctx.r3.u64 = kLanguageEnglish;
  }
}
