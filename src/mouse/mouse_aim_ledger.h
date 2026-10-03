// mouse_aim_ledger.h - carries unfinished mouse turns across camera frames.
#pragma once

#include <algorithm>

namespace ao2::mouse
{

  // Some camera-update routines don't integrate a turn rate; every frame they
  // recompute yaw/pitch from scratch (from an anchor orientation) and then let
  // only a fraction of the requested change through, easing the rest in over
  // several frames. Handing such a routine a raw per-sample mouse delta throws
  // most of a fast flick away, because the easing barely moves before the next
  // sample replaces the target entirely.
  //
  // MouseAimLedger keeps a running balance of "turn asked for but not yet
  // delivered" and keeps presenting it on top of the camera's own value every
  // frame, shrinking the balance by whatever the camera actually consumed
  // since the previous call. A long mouse flick then always resolves to the
  // same total turn, independent of how slowly the camera eases toward it or
  // how fast the game is running. Purely numeric: no knowledge of any
  // particular game's memory layout.
  class MouseAimLedger
  {
  public:
    // dyaw/dpitch are in the same units as Settle()'s yaw/pitch (radians
    // recommended), already scaled by sensitivity.
    void Credit(float dyaw, float dpitch)
    {
      balance_yaw_ = Bound(balance_yaw_ + dyaw);
      balance_pitch_ = Bound(balance_pitch_ + dpitch);
    }

    struct Result
    {
      float yaw;
      float pitch;
    };

    // Call once per camera-update frame, with the yaw/pitch the routine is
    // about to overwrite (read them before writing). idle_seconds is how long
    // it's been since the mouse last moved; once that passes
    // idle_release_seconds the balance is dropped so the game's own idle
    // behavior (auto-centering, etc.) takes back over instead of this ledger
    // holding a turn open forever.
    Result Settle(float yaw, float pitch, float idle_seconds, float idle_release_seconds)
    {
      if (primed_)
      {
        // Only what the camera didn't already act on since last time is still
        // owed - without this, a nearly-converged camera would get the full
        // balance added again and overshoot.
        balance_yaw_ = Bound(balance_yaw_ - (yaw - last_read_yaw_));
        balance_pitch_ = Bound(balance_pitch_ - (pitch - last_read_pitch_));
      }
      last_read_yaw_ = yaw;
      last_read_pitch_ = pitch;
      primed_ = true;

      if (idle_seconds >= idle_release_seconds)
      {
        balance_yaw_ = 0.0f;
        balance_pitch_ = 0.0f;
      }

      return Result{yaw + balance_yaw_, pitch + balance_pitch_};
    }

    void Reset()
    {
      balance_yaw_ = 0.0f;
      balance_pitch_ = 0.0f;
      primed_ = false;
    }

  private:
    static float Bound(float v)
    {
      // Finite but generous (a full turn either way), so a long pause between
      // Settle() calls can't build a balance that snaps the camera once
      // resolved.
      constexpr float kBound = 6.2831853f;
      return std::clamp(v, -kBound, kBound);
    }

    float balance_yaw_ = 0.0f;
    float balance_pitch_ = 0.0f;
    float last_read_yaw_ = 0.0f;
    float last_read_pitch_ = 0.0f;
    bool primed_ = false;
  };

} // namespace ao2::mouse
