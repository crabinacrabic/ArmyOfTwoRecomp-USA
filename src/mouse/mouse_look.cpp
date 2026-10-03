// mouse_look.cpp
#include "mouse_look.h"

#include <rex/cvar.h>
#include <rex/logging.h>

REXCVAR_DEFINE_BOOL(ao2_mouse_direct_look, false, "Mouse",
                    "Feed raw mouse motion straight to a camera-update hook instead of the "
                    "virtual right stick. Has no effect until such a hook exists for this "
                    "title - see src/mouse/mouse_look.h");
REXCVAR_DEFINE_DOUBLE(ao2_mouse_look_sensitivity, 0.0022, "Mouse",
                      "Camera radians per pixel of mouse motion when ao2_mouse_direct_look "
                      "is on")
    .range(0.0003, 0.02);
REXCVAR_DEFINE_BOOL(ao2_mouse_look_invert_y, false, "Mouse", "Invert the vertical look axis");
REXCVAR_DEFINE_INT32(ao2_mouse_look_idle_release_ms, 150, "Mouse",
                     "How long the mouse must sit still before an unfinished turn is dropped "
                     "and the title's own camera behavior (centering, etc.) resumes")
    .range(0, 1000);

namespace ao2::mouse
{

  namespace
  {
    // If Resolve() stops being called (the hook's frame didn't run - paused,
    // loading, a menu that doesn't update the camera) the pointer must not stay
    // hidden and locked with nothing consuming its motion.
    constexpr std::chrono::milliseconds kConsumerTimeout{500};
  } // namespace

  MouseLook &MouseLook::Get()
  {
    static MouseLook instance;
    return instance;
  }

  void MouseLook::Attach(rex::ui::Window *window)
  {
    window_ = window;
    if (!window_)
    {
      return;
    }
    window_->AddInputListener(this, 0);
    window_->AddListener(this);
  }

  void MouseLook::OnMouseMove(rex::ui::MouseEvent &e)
  {
    if (!capture_engaged_ || !has_focus_)
    {
      return;
    }
    if (ConsumerLooksStale())
    {
      SetCaptureEngaged(false);
      return;
    }
    std::lock_guard lock(motion_mutex_);
    pending_dx_ += e.dx();
    pending_dy_ += e.dy();
  }

  void MouseLook::OnLostFocus(rex::ui::UISetupEvent &)
  {
    has_focus_ = false;
    SetCaptureEngaged(false);
  }

  void MouseLook::OnGotFocus(rex::ui::UISetupEvent &)
  {
    has_focus_ = true;
  }

  void MouseLook::OnClosing(rex::ui::UIEvent &)
  {
    SetCaptureEngaged(false);
    window_ = nullptr;
  }

  bool MouseLook::ConsumerLooksStale() const
  {
    if (last_resolve_call_.time_since_epoch().count() == 0)
    {
      return false; // Resolve() was never called yet; nothing to time out.
    }
    return std::chrono::steady_clock::now() - last_resolve_call_ > kConsumerTimeout;
  }

  void MouseLook::SetCaptureEngaged(bool engaged)
  {
    if (engaged == capture_engaged_ || !window_)
    {
      return;
    }
    capture_engaged_ = engaged;
    if (engaged)
    {
      precapture_cursor_visibility_ = window_->GetCursorVisibility();
      window_->SetCursorVisibility(rex::ui::Window::CursorVisibility::kHidden);
      window_->CaptureMouse();
      if (!window_->SetRelativeMouseMode(true))
      {
        REXLOG_WARN("ao2_mouse_direct_look: this window backend has no pointer lock, falling "
                    "back to raw motion deltas without re-centering");
      }
      std::lock_guard lock(motion_mutex_);
      pending_dx_ = pending_dy_ = 0.0f;
      ledger_.Reset();
    }
    else
    {
      window_->SetRelativeMouseMode(false);
      window_->ReleaseMouse();
      window_->SetCursorVisibility(precapture_cursor_visibility_);
    }
  }

  std::optional<CameraAngles> MouseLook::Resolve(float current_yaw, float current_pitch,
                                                 float dt_seconds)
  {
    last_resolve_call_ = std::chrono::steady_clock::now();

    const bool enabled = REXCVAR_GET(ao2_mouse_direct_look) && has_focus_;
    SetCaptureEngaged(enabled);
    if (!enabled)
    {
      return std::nullopt;
    }

    float dx;
    float dy;
    {
      std::lock_guard lock(motion_mutex_);
      dx = pending_dx_;
      dy = pending_dy_;
      pending_dx_ = pending_dy_ = 0.0f;
    }

    const float sensitivity = static_cast<float>(REXCVAR_GET(ao2_mouse_look_sensitivity));
    const float pitch_sign = REXCVAR_GET(ao2_mouse_look_invert_y) ? 1.0f : -1.0f;
    ledger_.Credit(dx * sensitivity, dy * sensitivity * pitch_sign);

    idle_seconds_ = (dx == 0.0f && dy == 0.0f) ? idle_seconds_ + dt_seconds : 0.0f;
    const float idle_release_seconds =
        static_cast<float>(REXCVAR_GET(ao2_mouse_look_idle_release_ms)) / 1000.0f;

    const auto result = ledger_.Settle(current_yaw, current_pitch, idle_seconds_,
                                       idle_release_seconds);
    return CameraAngles{result.yaw, result.pitch};
  }

} // namespace ao2::mouse
