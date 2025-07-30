# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

# IMPORT BASE
# ///////////////////////////////////////////////////////////////
import re
import requests

# IMPORT SPECS
# ///////////////////////////////////////////////////////////////
from PySide6.QtCore import (
    Signal,
    Qt,
    QSize,
    QRect,
)
from PySide6.QtGui import (
    QIcon,
    QPainter,
    QPixmap,
    QColor,
    QMouseEvent,
    QPaintEvent,
)
from PySide6.QtWidgets import (
    QLineEdit,
    QVBoxLayout,
    QWidget,
    QProgressBar,
)

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////

# ////// TYPE HINTS IMPROVEMENTS FOR PYSIDE6 6.9.1
from typing import Optional, Union, Tuple

# UTILITY FUNCTIONS
# ///////////////////////////////////////////////////////////////


def password_strength(password: str) -> int:
    """Return a strength score from 0 (weak) to 100 (strong)."""
    score = 0
    if len(password) >= 8:
        score += 25
    if re.search(r"[A-Z]", password):
        score += 15
    if re.search(r"[a-z]", password):
        score += 15
    if re.search(r"\d", password):
        score += 20
    if re.search(r"[^A-Za-z0-9]", password):
        score += 25
    return min(score, 100)


def get_strength_color(score: int) -> str:
    """Return color based on password strength score."""
    if score < 30:
        return "#ff4444"  # Red
    elif score < 60:
        return "#ffaa00"  # Orange
    elif score < 80:
        return "#44aa44"  # Green
    else:
        return "#00aa00"  # Dark green


def colorize_pixmap(
    pixmap: QPixmap, color: str = "#FFFFFF", opacity: float = 0.5
) -> QPixmap:
    """Recolore un QPixmap avec la couleur et l'opacité données."""
    result = QPixmap(pixmap.size())
    result.fill(Qt.transparent)
    painter = QPainter(result)
    painter.setOpacity(opacity)
    painter.drawPixmap(0, 0, pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(result.rect(), QColor(color))
    painter.end()
    return result


def load_icon_from_source(source: Optional[Union[QIcon, str]]) -> Optional[QIcon]:
    """
    Load icon from various sources (QIcon, path, URL, etc.).

    Parameters
    ----------
    source : QIcon or str or None
        Icon source (QIcon, path, resource, URL, or SVG).

    Returns
    -------
    QIcon or None
        Loaded icon or None if failed.
    """
    # ////// HANDLE NONE
    if source is None:
        return None
    # ////// HANDLE QICON
    elif isinstance(source, QIcon):
        return source
    # ////// HANDLE STRING (PATH, URL, SVG)
    elif isinstance(source, str):

        # ////// HANDLE URL
        if source.startswith("http://") or source.startswith("https://"):
            print(f"Loading icon from URL: {source}")
            try:
                response = requests.get(source, timeout=5)
                response.raise_for_status()
                if "image" not in response.headers.get("Content-Type", ""):
                    raise ValueError("URL does not point to an image file.")
                image_data = response.content

                # ////// HANDLE SVG FROM URL
                if source.lower().endswith(".svg"):
                    from PySide6.QtSvg import QSvgRenderer
                    from PySide6.QtCore import QByteArray

                    renderer = QSvgRenderer(QByteArray(image_data))
                    pixmap = QPixmap(QSize(16, 16))
                    pixmap.fill(Qt.transparent)
                    painter = QPainter(pixmap)
                    renderer.render(painter)
                    painter.end()
                    return QIcon(pixmap)

                # ////// HANDLE RASTER IMAGE FROM URL
                else:
                    pixmap = QPixmap()
                    pixmap.loadFromData(image_data)
                    return QIcon(pixmap)

            except Exception as e:
                print(f"Failed to load icon from URL {source}: {e}")
                return None

        # ////// HANDLE LOCAL SVG
        elif source.lower().endswith(".svg"):
            from PySide6.QtSvg import QSvgRenderer

            renderer = QSvgRenderer(source)
            if renderer.isValid():
                pixmap = QPixmap(QSize(16, 16))
                pixmap.fill(Qt.transparent)
                painter = QPainter(pixmap)
                renderer.render(painter)
                painter.end()
                return QIcon(pixmap)
            else:
                print(f"Invalid SVG file: {source}")
                return None

        # ////// HANDLE LOCAL IMAGE
        else:
            pixmap = QPixmap(source)
            if not pixmap.isNull():
                return QIcon(pixmap)
            else:
                print(f"Failed to load image: {source}")
                return None

    # ////// FALLBACK
    return None


# CLASS
# ///////////////////////////////////////////////////////////////


class PasswordInput(QWidget):
    """
    Enhanced password input widget with integrated strength bar and right-side icon.

    Features:
        - QLineEdit in password mode with integrated strength bar
        - Right-side icon with click functionality
        - Icon management system (QIcon, path, URL, SVG)
        - Animated strength bar that fills the bottom border
        - Signal strengthChanged(int) emitted on password change
        - Color-coded strength indicator
        - External QSS styling support with CSS variables

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget (default: None).
    show_strength : bool, optional
        Whether to show the password strength bar (default: True).
    strength_bar_height : int, optional
        Height of the strength bar in pixels (default: 3).
    show_icon : str or QIcon, optional
        Icon for show password (default: "https://img.icons8.com/?size=100&id=85130&format=png&color=000000").
    hide_icon : str or QIcon, optional
        Icon for hide password (default: "https://img.icons8.com/?size=100&id=85137&format=png&color=000000").
    icon_size : QSize or tuple, optional
        Size of the icon (default: QSize(16, 16)).

    Properties
    ----------
    password : str
        Get or set the password text.
    show_strength : bool
        Get or set whether to show the strength bar.
    strength_bar_height : int
        Get or set the strength bar height.
    show_icon : QIcon
        Get or set the show password icon.
    hide_icon : QIcon
        Get or set the hide password icon.
    icon_size : QSize
        Get or set the icon size.

    Signals
    -------
    strengthChanged(int)
        Emitted when password strength changes.
    iconClicked()
        Emitted when the icon is clicked.
    """

    strengthChanged = Signal(int)
    iconClicked = Signal()

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(
        self,
        parent=None,
        show_strength: bool = True,
        strength_bar_height: int = 3,
        show_icon: Optional[
            Union[QIcon, str]
        ] = "https://img.icons8.com/?size=100&id=85130&format=png&color=000000",
        hide_icon: Optional[
            Union[QIcon, str]
        ] = "https://img.icons8.com/?size=100&id=85137&format=png&color=000000",
        icon_size: Union[QSize, Tuple[int, int]] = QSize(16, 16),
        *args,
        **kwargs,
    ):
        super().__init__(parent, *args, **kwargs)
        # ////// SET WIDGET TYPE FOR QSS SELECTION
        self.setProperty("type", "PasswordInput")
        # ////// SET OBJECT NAME FOR QSS SELECTION
        self.setObjectName("PasswordInput")

        # ////// INITIALIZE PROPERTIES
        self._show_strength: bool = show_strength
        self._strength_bar_height: int = strength_bar_height
        self._show_icon: Optional[QIcon] = None
        self._hide_icon: Optional[QIcon] = None
        self._show_icon_source: Optional[Union[QIcon, str]] = show_icon
        self._hide_icon_source: Optional[Union[QIcon, str]] = hide_icon
        self._icon_size: QSize = (
            QSize(icon_size) if isinstance(icon_size, (tuple, list)) else icon_size
        )
        self._current_strength: int = 0
        self._password_visible: bool = False

        # ////// SETUP UI
        self._setup_ui()

        # ////// SET ICONS
        if show_icon:
            self.show_icon = show_icon
        if hide_icon:
            self.hide_icon = hide_icon

        # ////// INITIALIZE ICON DISPLAY
        self._update_icon()

    def _setup_ui(self) -> None:
        """Setup the user interface components."""
        # ////// CREATE LAYOUT
        self._layout = QVBoxLayout(self)

        # ////// SET CONTENT MARGINS TO SHOW BORDERS
        self._layout.setContentsMargins(2, 2, 2, 2)
        self._layout.setSpacing(0)

        # ////// CREATE PASSWORD INPUT
        self._password_input = PasswordLineEdit()
        self._password_input.textChanged.connect(self.update_strength)

        # ////// CONNECT ICON CLICK SIGNAL
        self._password_input.iconClicked.connect(self.toggle_password)

        # ////// CREATE STRENGTH BAR
        self._strength_bar = QProgressBar()
        self._strength_bar.setProperty("type", "PasswordStrengthBar")
        self._strength_bar.setFixedHeight(self._strength_bar_height)
        self._strength_bar.setRange(0, 100)
        self._strength_bar.setValue(0)
        self._strength_bar.setTextVisible(False)
        self._strength_bar.setVisible(self._show_strength)

        # ////// ADD WIDGETS TO LAYOUT
        self._layout.addWidget(self._password_input)
        self._layout.addWidget(self._strength_bar)

    # UTILITY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def toggle_password(self) -> None:
        """Toggle password visibility."""
        self._password_visible = not self._password_visible
        if self._password_visible:
            self._password_input.setEchoMode(QLineEdit.Normal)
        else:
            self._password_input.setEchoMode(QLineEdit.Password)
        self._update_icon()

    def update_strength(self, text: str) -> None:
        """Update password strength."""
        score = password_strength(text)
        self._current_strength = score
        self._strength_bar.setValue(score)
        self._update_strength_color(score)
        self.strengthChanged.emit(score)

    def _update_icon(self) -> None:
        """Update the icon based on password visibility."""
        if self._password_visible and self._hide_icon:
            self._password_input.set_right_icon(self._hide_icon, self._icon_size)
        elif not self._password_visible and self._show_icon:
            self._password_input.set_right_icon(self._show_icon, self._icon_size)
        # ////// HANDLE CASE WHERE ICONS ARE NOT YET LOADED
        elif not self._password_visible and self._show_icon_source:
            # Try to load icon from source if not already loaded
            icon = load_icon_from_source(self._show_icon_source)
            if icon:
                self._show_icon = icon
                self._password_input.set_right_icon(icon, self._icon_size)

    def _update_strength_color(self, score: int) -> None:
        """Update strength bar color based on score."""
        color = get_strength_color(score)
        self._strength_bar.setStyleSheet(
            f"""
            QProgressBar {{
                border: none;
                background-color: #2d2d2d;
            }}
            QProgressBar::chunk {{
                background-color: {color};
            }}
            """
        )

    # PROPERTIES
    # ///////////////////////////////////////////////////////////////

    @property
    def password(self) -> str:
        """Get the password text."""
        return self._password_input.text()

    @password.setter
    def password(self, value: str) -> None:
        """Set the password text."""
        self._password_input.setText(str(value))

    @property
    def show_strength(self) -> bool:
        """Get whether the strength bar is shown."""
        return self._show_strength

    @show_strength.setter
    def show_strength(self, value: bool) -> None:
        """Set whether the strength bar is shown."""
        self._show_strength = bool(value)
        self._strength_bar.setVisible(self._show_strength)

    @property
    def strength_bar_height(self) -> int:
        """Get the strength bar height."""
        return self._strength_bar_height

    @strength_bar_height.setter
    def strength_bar_height(self, value: int) -> None:
        """Set the strength bar height."""
        self._strength_bar_height = max(1, int(value))
        self._strength_bar.setFixedHeight(self._strength_bar_height)

    @property
    def show_icon(self) -> Optional[QIcon]:
        """Get the show password icon."""
        return self._show_icon

    @show_icon.setter
    def show_icon(self, value: Optional[Union[QIcon, str]]) -> None:
        """Set the show password icon."""
        self._show_icon_source = value
        self._show_icon = load_icon_from_source(value)
        if not self._password_visible:
            self._update_icon()

    @property
    def hide_icon(self) -> Optional[QIcon]:
        """Get the hide password icon."""
        return self._hide_icon

    @hide_icon.setter
    def hide_icon(self, value: Optional[Union[QIcon, str]]) -> None:
        """Set the hide password icon."""
        self._hide_icon_source = value
        self._hide_icon = load_icon_from_source(value)
        if self._password_visible:
            self._update_icon()

    @property
    def icon_size(self) -> QSize:
        """Get the icon size."""
        return self._icon_size

    @icon_size.setter
    def icon_size(self, value: Union[QSize, Tuple[int, int]]) -> None:
        """Set the icon size."""
        self._icon_size = QSize(value) if isinstance(value, (tuple, list)) else value
        self._update_icon()

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refresh_style(self) -> None:
        """Refresh the widget style (deprecated - use external QSS)."""
        self.update()


class PasswordLineEdit(QLineEdit):
    """
    QLineEdit subclass with right-side icon support.

    Features:
        - Right-side icon with click functionality
        - Icon management system
        - Signal iconClicked emitted when icon is clicked
    """

    iconClicked = Signal()

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(self, parent=None):
        super().__init__(parent)
        # ////// SET WIDGET TYPE FOR QSS SELECTION
        self.setProperty("type", "PasswordInputField")
        self.setEchoMode(QLineEdit.Password)
        self._right_icon: Optional[QIcon] = None
        self._icon_rect: Optional[QRect] = None

    def set_right_icon(
        self, icon: Optional[QIcon], size: Optional[QSize] = None
    ) -> None:
        """Set the right-side icon."""
        self._right_icon = icon
        if size:
            self._icon_size = size
        else:
            self._icon_size = QSize(16, 16)
        self.update()

    # EVENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press events for icon clicking."""
        if (
            self._right_icon
            and self._icon_rect
            and self._icon_rect.contains(event.pos())
        ):
            self.iconClicked.emit()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move events for cursor changes."""
        if (
            self._right_icon
            and self._icon_rect
            and self._icon_rect.contains(event.pos())
        ):
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.IBeamCursor)
            super().mouseMoveEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Custom paint event to draw the right-side icon."""
        super().paintEvent(event)

        if not self._right_icon:
            return

        # ////// CALCULATE ICON POSITION
        icon_x = self.width() - self._icon_size.width() - 8
        icon_y = (self.height() - self._icon_size.height()) // 2

        self._icon_rect = QRect(
            icon_x, icon_y, self._icon_size.width(), self._icon_size.height()
        )

        # ////// DRAW ICON
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawPixmap(self._icon_rect, self._right_icon.pixmap(self._icon_size))

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refresh_style(self) -> None:
        """Refresh the widget's style (useful after dynamic stylesheet changes)."""
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
