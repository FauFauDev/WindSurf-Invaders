import pygame
from typing import Callable, Optional, Tuple


class LevelTransitionManager:
    """Handle smooth level transitions without blocking the game loop."""

    def __init__(
        self,
        fade_out_duration: int = 800,
        hold_duration: int = 800,
        fade_in_duration: int = 800,
        overlay_color: Tuple[int, int, int] = (8, 12, 26),
        text_color: Tuple[int, int, int] = (210, 240, 255),
    ) -> None:
        self.fade_out_duration = fade_out_duration
        self.hold_duration = hold_duration
        self.fade_in_duration = fade_in_duration
        self.overlay_color = overlay_color
        self.text_color = text_color

        # Runtime state
        self.active = False
        self.phase = "idle"
        self.phase_start = 0
        self.alpha = 0
        self.next_level = 0
        self.is_boss_level = False
        self.message = ""
        self.sub_message = ""
        self.prepare_callback: Optional[Callable[[], None]] = None
        self.prepare_called = False

        # Rendering helpers
        self._overlay_surface: Optional[pygame.Surface] = None
        self._title_font = pygame.font.Font(None, 96)
        self._subtitle_font = pygame.font.Font(None, 42)

    def reset(self) -> None:
        """Return to idle state and clear any pending transition."""
        self.active = False
        self.phase = "idle"
        self.alpha = 0
        self.next_level = 0
        self.is_boss_level = False
        self.message = ""
        self.sub_message = ""
        self.prepare_callback = None
        self.prepare_called = False

    def start(
        self,
        next_level: int,
        is_boss_level: bool,
        prepare_callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """Start a new transition sequence."""
        if self.active:
            return

        self.active = True
        self.phase = "fade_out"
        self.phase_start = pygame.time.get_ticks()
        self.alpha = 0
        self.next_level = next_level
        self.is_boss_level = is_boss_level
        self.prepare_callback = prepare_callback
        self.prepare_called = False

        if is_boss_level:
            self.message = "BOSS APPROACHING"
            self.sub_message = f"Prepare for Level {next_level}"
        else:
            self.message = f"Level {next_level}"
            self.sub_message = "Prepare for the next wave"

    def update(self, current_time: Optional[int] = None) -> None:
        """Advance the transition state machine."""
        if not self.active:
            return

        if current_time is None:
            current_time = pygame.time.get_ticks()

        elapsed = current_time - self.phase_start

        if self.phase == "fade_out":
            progress = min(1.0, elapsed / self.fade_out_duration) if self.fade_out_duration else 1.0
            self.alpha = int(255 * progress)
            if progress >= 1.0:
                self.phase = "hold"
                self.phase_start = current_time
        elif self.phase == "hold":
            self.alpha = 255
            if not self.prepare_called and self.prepare_callback:
                self.prepare_callback()
                self.prepare_called = True
            if elapsed >= self.hold_duration:
                self.phase = "fade_in"
                self.phase_start = current_time
        elif self.phase == "fade_in":
            progress = min(1.0, elapsed / self.fade_in_duration) if self.fade_in_duration else 1.0
            self.alpha = int(255 * (1.0 - progress))
            if progress >= 1.0:
                self.reset()

    def draw(self, surface: pygame.Surface) -> None:
        """Render the transition overlay and messages."""
        if not self.active and self.alpha <= 0:
            return

        if self._overlay_surface is None or self._overlay_surface.get_size() != surface.get_size():
            self._overlay_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)

        overlay_alpha = max(0, min(255, self.alpha))
        self._overlay_surface.fill((*self.overlay_color, overlay_alpha))
        surface.blit(self._overlay_surface, (0, 0))

        if not self.message:
            return

        # Fade text in slightly faster for better readability
        text_alpha = max(0, min(255, overlay_alpha + 40))

        title_surface = self._title_font.render(self.message, True, self.text_color)
        title_surface.set_alpha(text_alpha)
        title_rect = title_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 - 30))
        surface.blit(title_surface, title_rect)

        if self.sub_message:
            subtitle_surface = self._subtitle_font.render(self.sub_message, True, self.text_color)
            subtitle_surface.set_alpha(text_alpha)
            subtitle_rect = subtitle_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 + 30))
            surface.blit(subtitle_surface, subtitle_rect)

    @property
    def is_active(self) -> bool:
        return self.active
