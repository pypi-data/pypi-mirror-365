# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

# IMPORT BASE
# ///////////////////////////////////////////////////////////////

# IMPORT SPECS
# ///////////////////////////////////////////////////////////////
from PySide6.QtCore import (
    Qt,
    QSize,
    Signal,
    QPropertyAnimation,
    QEasingCurve,
    Property,
    QRect,
)
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPen,
    QBrush,
    QMouseEvent,
    QPaintEvent,
)
from PySide6.QtWidgets import (
    QWidget,
    QSizePolicy,
)

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////

# ////// TYPE HINTS IMPROVEMENTS FOR PYSIDE6 6.9.1

# UTILITY FUNCTIONS
# ///////////////////////////////////////////////////////////////

# CLASS
# ///////////////////////////////////////////////////////////////


class ToggleSwitch(QWidget):
    """
    Modern toggle switch widget with animated sliding circle.

    Features:
        - Smooth animation when toggling
        - Customizable colors for on/off states
        - Configurable size and border radius
        - Click to toggle functionality
        - Property-based access to state
        - Signal emitted on state change

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget (default: None).
    checked : bool, optional
        Initial state of the toggle (default: False).
    width : int, optional
        Width of the toggle switch (default: 50).
    height : int, optional
        Height of the toggle switch (default: 24).
    animation : bool, optional
        Whether to animate the toggle (default: True).
    *args, **kwargs :
        Additional arguments passed to QWidget.

    Properties
    ----------
    checked : bool
        Get or set the toggle state.
    width : int
        Get or set the width of the toggle.
    height : int
        Get or set the height of the toggle.
    animation : bool
        Get or set whether animation is enabled.

    Signals
    -------
    toggled(bool)
        Emitted when the toggle state changes.
    """

    toggled = Signal(bool)

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(
        self,
        parent=None,
        checked: bool = False,
        width: int = 50,
        height: int = 24,
        animation: bool = True,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)

        # ////// INITIALIZE PROPERTIES
        self._checked: bool = checked
        self._width: int = width
        self._height: int = height
        self._animation: bool = animation
        self._circle_radius: int = (height - 4) // 2  # Circle radius with 2px margin
        self._animation_duration: int = 200

        # ////// COLORS
        self._bg_color_off: QColor = QColor(44, 49, 58)  # Default dark theme
        self._bg_color_on: QColor = QColor(150, 205, 50)  # Default accent color
        self._circle_color: QColor = QColor(255, 255, 255)
        self._border_color: QColor = QColor(52, 59, 72)

        # ////// INITIALIZE POSITION
        self._circle_position: int = self._get_circle_position()

        # ////// SETUP ANIMATION
        self._setup_animation()

        # ////// SETUP WIDGET
        self._setup_widget()

    def _setup_animation(self) -> None:
        """Setup the animation system."""
        self._animation_obj = QPropertyAnimation(self, b"circle_position")
        self._animation_obj.setDuration(self._animation_duration)
        self._animation_obj.setEasingCurve(QEasingCurve.InOutQuart)

    def _setup_widget(self) -> None:
        """Setup the widget properties."""
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedSize(self._width, self._height)
        self.setCursor(Qt.PointingHandCursor)

    def _get_circle_position(self) -> int:
        """Calculate circle position based on state."""
        if self._checked:
            return self._width - self._height + 2  # Right position
        else:
            return 2  # Left position

    def _get_circle_position_property(self) -> int:
        """Property getter for animation."""
        return self._circle_position

    def _set_circle_position_property(self, position: int) -> None:
        """Property setter for animation."""
        self._circle_position = position
        self.update()

    # Property for animation
    circle_position = Property(
        int, _get_circle_position_property, _set_circle_position_property
    )

    # PROPERTIES
    # ///////////////////////////////////////////////////////////////

    @property
    def checked(self) -> bool:
        """Get the toggle state."""
        return self._checked

    @checked.setter
    def checked(self, value: bool) -> None:
        """Set the toggle state."""
        if value != self._checked:
            self._checked = bool(value)
            if self._animation:
                self._animate_circle()
            else:
                self._circle_position = self._get_circle_position()
                self.update()
            self.toggled.emit(self._checked)

    @property
    def width(self) -> int:
        """Get the width of the toggle."""
        return self._width

    @width.setter
    def width(self, value: int) -> None:
        """Set the width of the toggle."""
        self._width = max(20, int(value))
        self._circle_radius = (self._height - 4) // 2
        self.setFixedSize(self._width, self._height)
        self._circle_position = self._get_circle_position()
        self.update()

    @property
    def height(self) -> int:
        """Get the height of the toggle."""
        return self._height

    @height.setter
    def height(self, value: int) -> None:
        """Set the height of the toggle."""
        self._height = max(12, int(value))
        self._circle_radius = (self._height - 4) // 2
        self.setFixedSize(self._width, self._height)
        self._circle_position = self._get_circle_position()
        self.update()

    @property
    def animation(self) -> bool:
        """Get whether animation is enabled."""
        return self._animation

    @animation.setter
    def animation(self, value: bool) -> None:
        """Set whether animation is enabled."""
        self._animation = bool(value)

    # UTILITY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def _animate_circle(self) -> None:
        """Animate the circle movement."""
        target_position = self._get_circle_position()
        self._animation_obj.setStartValue(self._circle_position)
        self._animation_obj.setEndValue(target_position)
        self._animation_obj.start()

    def toggle(self) -> None:
        """Toggle the switch state."""
        self.checked = not self._checked

    # EVENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            self.toggle()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Custom paint event to draw the toggle switch."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # ////// DRAW BACKGROUND
        bg_color = self._bg_color_on if self._checked else self._bg_color_off
        painter.setPen(QPen(self._border_color, 1))
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(
            0, 0, self._width, self._height, self._height // 2, self._height // 2
        )

        # ////// DRAW CIRCLE
        circle_x = self._circle_position
        circle_y = (self._height - self._circle_radius * 2) // 2
        circle_rect = QRect(
            circle_x, circle_y, self._circle_radius * 2, self._circle_radius * 2
        )

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self._circle_color))
        painter.drawEllipse(
            circle_x, circle_y, circle_rect.width(), circle_rect.height()
        )

    # OVERRIDE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def sizeHint(self) -> QSize:
        """Return the recommended size for the widget."""
        return QSize(self._width, self._height)

    def minimumSizeHint(self) -> QSize:
        """Return the minimum size for the widget."""
        return QSize(self._width, self._height)

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refresh_style(self) -> None:
        """Refresh the widget style."""
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
