import tkinter as tk
import numpy as np
from config.colors import COLORS


class AnalogVUMeter(tk.Canvas):
    """Analog VU meter with realistic needle bounce physics."""

    def __init__(self, parent, width: int = 140, height: int = 100,
                 color: str = None, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=COLORS['meter_bg'], highlightthickness=0, **kwargs)

        self.width = width
        self.height = height
        self.color = color or COLORS['accent']

        self.target_level = 0.0
        self.current_level = 0.0
        self.needle_velocity = 0.0

        self.attack_speed = 0.2
        self.decay_speed = 0.04
        self.damping = 0.82
        self.spring_constant = 0.35

        self.center_x = width // 2
        self.center_y = height // 2 + 5
        self.radius = min(width, height) // 2 - 12

        self.start_angle = 225
        self.end_angle = 315
        self.angle_range = self.end_angle - self.start_angle

        self.needle_length = self.radius - 8

        self.isAnimating = False
        self.animation_id = None

        self._draw()

    def set_level(self, level):
        """Set VU meter target level and start animation."""
        self.target_level = max(0.0, min(1.0, level))
        # Always start animation to move needle toward target
        if not self.isAnimating:
            self._start_animation()

    def _start_animation(self):
        self.isAnimating = True
        self._animate_needle()

    def _stop_animation(self):
        self.isAnimating = False
        if self.animation_id is not None:
            self.after_cancel(self.animation_id)
            self.animation_id = None

    def _animate_needle(self):
        if not self.isAnimating:
            return

        error = self.target_level - self.current_level
        spring_force = error * self.spring_constant

        if error > 0:
            self.needle_velocity += spring_force * self.attack_speed
        else:
            self.needle_velocity += spring_force * self.decay_speed

        self.needle_velocity *= self.damping
        self.current_level += self.needle_velocity
        self.current_level = max(0.0, min(1.0, self.current_level))

        self._draw()

        if abs(self.needle_velocity) > 0.001 or abs(error) > 0.01:
            self.animation_id = self.after(16, self._animate_needle)
        else:
            self.isAnimating = False

    def _draw(self):
        self.delete('all')

        self.create_oval(2, 2, self.width - 2, self.height - 2,
                        fill=COLORS['fader_track'], outline='#222222', width=2)
        self.create_oval(8, 8, self.width - 8, self.height - 8,
                        fill='#0f0f0f', outline='#1a1a1a', width=1)

        self._draw_colored_arc()
        self._draw_tick_marks()
        self._draw_labels()
        self._draw_needle()

        self.create_oval(self.center_x - 8, self.center_y - 8,
                        self.center_x + 8, self.center_y + 8,
                        fill='#2a2a2a', outline='#444444', width=2)
        self.create_oval(self.center_x - 4, self.center_y - 4,
                        self.center_x + 4, self.center_y + 4,
                        fill='#555555', outline='#666666', width=1)

    def _draw_colored_arc(self):
        green_end = self.start_angle + self.angle_range * 0.7
        self.create_arc(8, 8, self.width - 8, self.height - 8,
                       start=self.start_angle, extent=green_end - self.start_angle,
                       style='arc', outline=COLORS['led_green'], width=5)

        yellow_end = self.start_angle + self.angle_range * 0.85
        self.create_arc(8, 8, self.width - 8, self.height - 8,
                       start=green_end, extent=yellow_end - green_end,
                       style='arc', outline=COLORS['led_yellow'], width=5)

        self.create_arc(8, 8, self.width - 8, self.height - 8,
                       start=yellow_end, extent=self.end_angle - yellow_end,
                       style='arc', outline=COLORS['led_red'], width=5)

    def _draw_tick_marks(self):
        for i in range(11):
            angle = self.start_angle + (i / 10) * self.angle_range
            angle_rad = np.radians(angle)
            inner_r = self.radius - 5
            outer_r = self.radius + 5
            x1 = self.center_x + inner_r * np.cos(angle_rad)
            y1 = self.center_y - inner_r * np.sin(angle_rad)
            x2 = self.center_x + outer_r * np.cos(angle_rad)
            y2 = self.center_y - outer_r * np.sin(angle_rad)
            self.create_line(x1, y1, x2, y2, fill=COLORS['fg_dim'], width=1)

    def _draw_labels(self):
        labels = [-20, -10, -7, -5, -3, 0, +1, +2, +3]
        self._db_min = labels[0]   # -20 dB at needle position 0.0
        self._db_max = labels[-1]  # +3 dB at needle position 1.0
        for i, db in enumerate(labels):
            angle = self.start_angle + (i / (len(labels) - 1)) * self.angle_range
            angle_rad = np.radians(angle)
            label_r = self.radius + 14
            x = self.center_x + label_r * np.cos(angle_rad)
            y = self.center_y - label_r * np.sin(angle_rad)
            color = COLORS['led_green'] if db < 0 else COLORS['led_yellow'] if db < 2 else COLORS['led_red']
            self.create_text(x, y, text=str(db), fill=color, font=('', 7))

    def _draw_needle(self):
        """Draw needle with glow effect."""
        angle = self.start_angle + self.current_level * self.angle_range
        angle_rad = np.radians(angle)
        tip_x = self.center_x + self.needle_length * np.cos(angle_rad)
        tip_y = self.center_y - self.needle_length * np.sin(angle_rad)

        # Outer glow (large, dim)
        self.create_line(self.center_x, self.center_y, tip_x, tip_y,
                        fill='#440000', width=12, capstyle='round')
        # Middle glow
        self.create_line(self.center_x, self.center_y, tip_x, tip_y,
                        fill='#661111', width=8, capstyle='round')
        # Inner glow
        self.create_line(self.center_x, self.center_y, tip_x, tip_y,
                        fill='#882222', width=5, capstyle='round')
        # Main needle body
        self.create_line(self.center_x, self.center_y, tip_x, tip_y,
                        fill='#ff2222', width=3, capstyle='round')
        # Bright highlight
        self.create_line(self.center_x, self.center_y, tip_x, tip_y,
                        fill='#ff6666', width=1, capstyle='round')
