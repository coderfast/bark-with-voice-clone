import tkinter as tk
from config.colors import COLORS


class MixerFader(tk.Canvas):
    """Custom mixer-style fader widget."""

    def __init__(self, parent, variable: tk.DoubleVar, from_: float = 0.0,
                 to: float = 1.0, width: int = 60, height: int = 150,
                 orientation: str = 'vertical', color: str = None,
                 on_release: callable = None, on_press: callable = None, **kwargs):
        """Initialize mixer fader.

        Args:
            parent: Parent widget
            variable: Tkinter variable to bind
            from_: Minimum value
            to: Maximum value
            width: Widget width
            height: Widget height
            orientation: 'vertical' or 'horizontal'
            color: Accent color
            on_release: Callback when slider is released
            on_press: Callback when slider is pressed
        """
        super().__init__(parent, width=width, height=height,
                         bg=COLORS['channel_bg'], highlightthickness=0, **kwargs)

        self.variable = variable
        self.from_ = from_
        self.to = to
        self.width = width
        self.height = height
        self.orientation = orientation
        self.color = color or COLORS['accent']
        self.on_release = on_release
        self.on_press = on_press
        self.isDragging = False
        self.audio_level = 0.0  # External audio level for animation

        # Fader dimensions
        self.track_width = 8
        self.thumb_width = 30
        self.thumb_height = 12
        self.led_count = 10

        # Calculate track bounds
        if orientation == 'vertical':
            self.track_x = (width - self.track_width) // 2
            self.track_top = 20
            self.track_bottom = height - 20
            self.track_height = self.track_bottom - self.track_top
        else:
            self.track_y = (height - self.track_width) // 2
            self.track_left = 20
            self.track_right = width - 20
            self.track_width_actual = self.track_right - self.track_left

        # Draw initial state
        self._draw()

        # Bind events
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<B1-Motion>', self._on_drag)
        self.bind('<ButtonRelease-1>', self._on_release)

    def set_audio_level(self, level: float) -> None:
        """Set audio level for meter animation (0.0 to 1.0)."""
        self.audio_level = max(0.0, min(1.0, level))
        self._draw()

    def _value_to_position(self, value: float) -> float:
        """Convert value to pixel position."""
        if self.orientation == 'vertical':
            # Invert for vertical (top = max, bottom = min)
            normalized = (value - self.from_) / (self.to - self.from_)
            return self.track_bottom - (normalized * self.track_height)
        else:
            normalized = (value - self.from_) / (self.to - self.from_)
            return self.track_left + (normalized * self.track_width_actual)

    def _position_to_value(self, pos: float) -> float:
        """Convert pixel position to value."""
        if self.orientation == 'vertical':
            normalized = (self.track_bottom - pos) / self.track_height
        else:
            normalized = (pos - self.track_left) / self.track_width_actual
        normalized = max(0.0, min(1.0, normalized))
        return self.from_ + (normalized * (self.to - self.from_))

    def _draw(self):
        """Draw the fader."""
        self.delete('all')

        if self.orientation == 'vertical':
            self._draw_vertical()
        else:
            self._draw_horizontal()

    def _draw_vertical(self):
        """Draw vertical fader with professional mixer styling."""
        # Draw LED meter on the right side (uses audio_level for animation)
        led_x = self.track_x + self.track_width + 8

        for i in range(self.led_count):
            led_y = self.track_top + (i * self.track_height / self.led_count)
            led_h = self.track_height / self.led_count - 2

            # Determine LED color based on audio level
            if i / self.led_count > self.audio_level:
                color = COLORS['led_off']
            elif i < 6:
                color = COLORS['led_green']
            elif i < 8:
                color = COLORS['led_yellow']
            else:
                color = COLORS['led_red']

            self.create_rectangle(led_x, led_y, led_x + 6, led_y + led_h,
                                fill=color, outline='#0a0a0a', width=1)

        # Draw track background with metallic look
        self.create_rectangle(
            self.track_x - 1, self.track_top - 1,
            self.track_x + self.track_width + 1, self.track_bottom + 1,
            fill='#0a0a0a', outline='#111111'
        )

        # Draw track groove with depth effect
        self.create_rectangle(
            self.track_x, self.track_top,
            self.track_x + self.track_width, self.track_bottom,
            fill=COLORS['fader_track'], outline=COLORS['fader_groove']
        )

        # Draw center line
        center_y = self.track_top + self.track_height // 2
        self.create_line(
            self.track_x + 1, center_y,
            self.track_x + self.track_width - 1, center_y,
            fill=COLORS['fader_groove'], width=1
        )

        # Draw groove marks
        for i in range(21):
            y = self.track_top + (i * self.track_height / 20)
            self.create_line(
                self.track_x + 1, y,
                self.track_x + self.track_width - 1, y,
                fill=COLORS['fader_groove'] if i % 5 != 0 else COLORS['channel_border']
            )

        # Calculate thumb position
        thumb_pos = self._value_to_position(self.variable.get())
        thumb_x = self.track_x + self.track_width // 2 - self.thumb_width // 2
        thumb_y = thumb_pos - self.thumb_height // 2

        # Draw thumb shadow
        self.create_rectangle(
            thumb_x + 1, thumb_y + 1,
            thumb_x + self.thumb_width + 1, thumb_y + self.thumb_height + 1,
            fill='#000000', outline=''
        )

        # Draw thumb body with metallic gradient effect
        thumb_color = COLORS['fader_thumb_active'] if self.isDragging else COLORS['fader_thumb']
        self.create_rectangle(
            thumb_x, thumb_y,
            thumb_x + self.thumb_width, thumb_y + self.thumb_height,
            fill=thumb_color, outline=COLORS['fader_thumb_edge'], width=1
        )

        # Draw thumb highlight (top edge)
        self.create_line(
            thumb_x + 1, thumb_y + 1,
            thumb_x + self.thumb_width - 1, thumb_y + 1,
            fill='#666666'
        )

        # Draw thumb grip lines (concave groove effect)
        grip_y_center = thumb_y + self.thumb_height // 2
        for offset in [-3, -1, 1, 3]:
            self.create_line(
                thumb_x + 4, grip_y_center + offset,
                thumb_x + self.thumb_width - 4, grip_y_center + offset,
                fill='#333333'
            )

    def _draw_horizontal(self):
        """Draw horizontal fader."""
        # Draw track background
        self.create_rectangle(
            self.track_left, self.track_y,
            self.track_right, self.track_y + self.track_width,
            fill=COLORS['fader_track'], outline=COLORS['fader_groove']
        )

        # Draw track groove lines
        for i in range(11):
            x = self.track_left + (i * self.track_width_actual / 10)
            self.create_line(
                x, self.track_y + 2,
                x, self.track_y + self.track_width - 2,
                fill=COLORS['fader_groove']
            )

        # Calculate thumb position
        thumb_pos = self._value_to_position(self.variable.get())
        thumb_x = thumb_pos - self.thumb_height // 2
        thumb_y = self.track_y + self.track_width // 2 - self.thumb_width // 2

        # Draw thumb shadow
        self.create_rectangle(
            thumb_x + 2, thumb_y + 2,
            thumb_x + self.thumb_height + 2, thumb_y + self.thumb_width + 2,
            fill='#1a1a1a', outline=''
        )

        # Draw thumb body
        thumb_color = COLORS['fader_thumb_active'] if self.isDragging else COLORS['fader_thumb']
        self.create_rectangle(
            thumb_x, thumb_y,
            thumb_x + self.thumb_height, thumb_y + self.thumb_width,
            fill=thumb_color, outline='#555555', width=1
        )

        # Draw thumb grip lines
        grip_x_center = thumb_x + self.thumb_height // 2
        for offset in [-2, 0, 2]:
            self.create_line(
                grip_x_center + offset, thumb_y + 5,
                grip_x_center + offset, thumb_y + self.thumb_width - 5,
                fill='#444444'
            )

    def _on_press(self, event):
        """Handle mouse press."""
        self.isDragging = True
        if self.on_press:
            self.on_press()
        self._update_value(event)
        self._draw()

    def _on_drag(self, event):
        """Handle mouse drag."""
        if self.isDragging:
            self._update_value(event)
            self._draw()

    def _on_release(self, event):
        """Handle mouse release."""
        self.isDragging = False
        self._update_value(event)
        self._draw()
        if self.on_release:
            self.on_release()

    def _update_value(self, event):
        """Update value from mouse position."""
        if self.orientation == 'vertical':
            value = self._position_to_value(event.y)
        else:
            value = self._position_to_value(event.x)
        self.variable.set(round(value, 2))

    def set_value(self, value: float):
        """Set fader value programmatically."""
        self.variable.set(value)
        self._draw()
