// mouse_look.h - optional direct mouse-to-camera path, bypassing the
// emulated right stick.
//
// The keyboard/mouse-to-pad driver (thirdparty/rexglue-sdk's mnk driver)
// turns mouse motion into right-stick deflection, which then runs through
// whatever deadzone/acceleration curve the title applies to a real stick.
// That's fine for a controller stand-in, but it means the mouse never feels
// like a mouse: there's a dead patch near the center and a soft response
// everywhere else, both designed for thumbsticks.
//
// This module is for the alternative: once a title's camera-update routine
// has been located (reverse engineering, out of scope for this file), a
// patch can read the camera's yaw/pitch, call Resolve() with them, and write
// the returned angles back - handing the camera raw, 1:1 mouse motion
// instead of a fake stick signal. MouseAimLedger (mouse_aim_ledger.h) makes
// that safe even for cameras that re-derive their yaw/pitch from an anchor
// every frame instead of integrating a rate.
//
// Self-contained by design, so the whole src/mouse/ folder can be copied
// into another ReXGlue-based project as-is: it only talks to rex::ui::Window
// and rex::cvar, never to this game's own generated headers. The only
// per-project wiring needed is:
//   1. one call to MouseLook::Get().Attach(window()) once the window exists
//      (see ArmyoftworecompApp::OnCreateDialogs in armyoftworecomp_app.h);
//   2. once a camera-update hook exists for the title, a call to Resolve()
///     from inside it (see the worked example at the bottom of this file).
//
// Until step 2 happens for a given game, the feature is inert: the cvar
// below does nothing, the mouse is never captured, and the mnk driver keeps
// working exactly as before.
#pragma once

#include <rex/ui/window.h>
#include <rex/ui/window_listener.h>

#include <chrono>
#include <cstdint>
#include <mutex>
#include <optional>

#include "mouse_aim_ledger.h"

namespace ao2::mouse
{

  struct CameraAngles
  {
    float yaw;
    float pitch;
  };

  class MouseLook final : public rex::ui::WindowInputListener, public rex::ui::WindowListener
  {
  public:
    static MouseLook &Get();

    MouseLook(const MouseLook &) = delete;
    MouseLook &operator=(const MouseLook &) = delete;

    // Call once, after the main window has opened.
    void Attach(rex::ui::Window *window);

    // Call every frame from the camera-update hook, with the yaw/pitch it is
    // about to overwrite (read them first). dt_seconds is this frame's delta
    // time, used only to time the idle release. Returns the angles to write
    // back, or nullopt when the feature is off (ao2_mouse_direct_look) or the
    // window lost focus - write nothing in that case and let the title's own
    // update run unmodified.
    std::optional<CameraAngles> Resolve(float current_yaw, float current_pitch, float dt_seconds);

    // rex::ui::WindowInputListener
    void OnMouseMove(rex::ui::MouseEvent &e) override;

    // rex::ui::WindowListener
    void OnLostFocus(rex::ui::UISetupEvent &) override;
    void OnGotFocus(rex::ui::UISetupEvent &) override;
    void OnClosing(rex::ui::UIEvent &) override;

  private:
    MouseLook() = default;

    void SetCaptureEngaged(bool engaged);
    bool ConsumerLooksStale() const;

    rex::ui::Window *window_ = nullptr;
    bool capture_engaged_ = false;
    bool has_focus_ = true;
    rex::ui::Window::CursorVisibility precapture_cursor_visibility_ =
        rex::ui::Window::CursorVisibility::kVisible;

    std::mutex motion_mutex_;
    float pending_dx_ = 0.0f;
    float pending_dy_ = 0.0f;

    MouseAimLedger ledger_;
    float idle_seconds_ = 0.0f;
    std::chrono::steady_clock::time_point last_resolve_call_{};
  };

} // namespace ao2::mouse

// --- Worked example (nothing below this point is compiled) ---
//
// Once a camera-update routine is identified for this title (typically a
// function that runs once per frame per camera and carries yaw/pitch as
// fields on some "r3"/"r31"-style object pointer), wire it up along these
// lines from game_patches.cpp or a dedicated hook file:
//
//   void CameraUpdateHook(PPCRegister& r31) {
//     auto* memory = REX_KERNEL_MEMORY();
//     uint8_t* yaw_ptr = memory->TranslateVirtual<uint8_t*>(r31.u32 + kYawOffset);
//     uint8_t* pitch_ptr = memory->TranslateVirtual<uint8_t*>(r31.u32 + kPitchOffset);
//     float yaw = rex::memory::load_and_swap<float>(yaw_ptr);
//     float pitch = rex::memory::load_and_swap<float>(pitch_ptr);
//     if (auto angles = ao2::mouse::MouseLook::Get().Resolve(yaw, pitch, FrameDeltaSeconds())) {
//       rex::memory::store_and_swap<float>(yaw_ptr, angles->yaw);
//       rex::memory::store_and_swap<float>(pitch_ptr, angles->pitch);
//     }
//   }
//
// kYawOffset/kPitchOffset and the hook point itself are game-specific and
// need to be found with a disassembler; nothing in this file guesses them.
