# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

# IMPORT BASE
# ///////////////////////////////////////////////////////////////
import requests

# IMPORT SPECS
# ///////////////////////////////////////////////////////////////
from PySide6.QtCore import (
    Signal,
    Qt,
    QSize,
    QRect,
    QEvent,
)
from PySide6.QtGui import (
    QPainter,
    QIcon,
    QPixmap,
    QColor,
    QMouseEvent,
    QPaintEvent,
    QResizeEvent,
    QEnterEvent,
)
from PySide6.QtWidgets import (
    QLabel,
)

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////

# ////// TYPE HINTS IMPROVEMENTS FOR PYSIDE6 6.9.1
from typing import Optional, Union, Tuple

# UTILITY FUNCTIONS
# ///////////////////////////////////////////////////////////////

# CLASS
# ///////////////////////////////////////////////////////////////


class HoverLabel(QLabel):
    """
    HoverLabel is an interactive QLabel that displays a floating icon when hovered, and emits a signal when the icon is clicked.

    This widget is useful for adding contextual actions or visual cues to labels in a Qt interface.

    Features:
        - Displays a custom icon on hover, with configurable opacity, size, color overlay, and padding
        - Emits a hoverIconClicked signal when the icon is clicked
        - Handles mouse events and cursor changes for better UX
        - Text and icon can be set at construction or via properties
        - Icon can be enabled/disabled dynamically
        - Supports PNG/JPG and SVG icons (local, resource, URL)
        - Robust error handling for icon loading

    Example
    -------
    >>> label = HoverLabel(text="Survolez-moi !", icon="/path/to/icon.png", icon_color="#00BFFF")
    >>> label.icon_enabled = True
    >>> label.icon_padding = 12
    >>> label.clear_icon()

    Use cases
    ---------
    - Contextual action button in a label
    - Info or help icon on hover
    - Visual feedback for interactive labels

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget (default: None).
    icon : QIcon or str, optional
        The icon to display on hover (QIcon, path, resource, URL, or SVG).
    text : str, optional
        The label text (default: "").
    opacity : float, optional
        The opacity of the hover icon (default: 0.5).
    icon_size : QSize or tuple, optional
        The size of the hover icon (default: QSize(16, 16)).
    icon_color : QColor or str, optional
        Optional color overlay to apply to the icon (default: None).
    icon_padding : int, optional
        Padding (in px) to the right of the text for the icon (default: 8).
    icon_enabled : bool, optional
        Whether the icon is shown on hover (default: True).
    min_width : int, optional
        Minimum width of the widget (default: None).
    *args, **kwargs :
        Additional arguments passed to QLabel.

    Properties
    ----------
    opacity : float
        Get or set the opacity of the hover icon.
    hover_icon : QIcon
        Get or set the icon displayed on hover.
    icon_size : QSize
        Get or set the size of the hover icon.
    icon_color : QColor or str or None
        Get or set the color overlay of the hover icon.
    icon_padding : int
        Get or set the right padding for the icon.
    icon_enabled : bool
        Enable or disable the hover icon.

    Signals
    -------
    hoverIconClicked()
        Emitted when the hover icon is clicked.
    """

    hoverIconClicked = Signal()  # Signal personnalisé

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(
        self,
        parent=None,
        icon: Optional[Union[QIcon, str]] = None,
        text: str = "",
        opacity: float = 0.5,
        icon_size: Union[QSize, Tuple[int, int]] = QSize(16, 16),
        icon_color: Optional[Union[QColor, str]] = None,
        icon_padding: int = 8,
        icon_enabled: bool = True,
        min_width: Optional[int] = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, text=text or "", **kwargs)
        self.setProperty("type", "HoverLabel")

        # ////// INITIALIZE PROPERTIES
        self._opacity: float = opacity
        self._hover_icon: Optional[QIcon] = None
        self._icon_size: QSize = (
            QSize(icon_size) if isinstance(icon_size, (tuple, list)) else icon_size
        )
        self._icon_color: Optional[Union[QColor, str]] = icon_color
        self._icon_padding: int = icon_padding
        self._icon_enabled: bool = icon_enabled
        self._min_width: Optional[int] = min_width

        # ////// STATE VARIABLES
        self._show_hover_icon: bool = False

        # ////// SETUP WIDGET
        self.setMouseTracking(True)
        self.setCursor(Qt.ArrowCursor)

        # ////// SET MINIMUM WIDTH
        if self._min_width:
            self.setMinimumWidth(self._min_width)

        # ////// SET ICON (setter gère tout)
        if icon:
            self.hover_icon = icon

    # PROPERTIES
    # ///////////////////////////////////////////////////////////////

    @property
    def opacity(self) -> float:
        """Get the opacity of the hover icon."""
        return self._opacity

    @opacity.setter
    def opacity(self, value: float) -> None:
        """Set the opacity of the hover icon."""
        self._opacity = float(value)
        self.update()

    @property
    def hover_icon(self) -> Optional[QIcon]:
        """Get the hover icon."""
        return self._hover_icon

    @hover_icon.setter
    def hover_icon(self, value: Optional[Union[QIcon, str]]) -> None:
        """Set the icon displayed on hover. Accepts QIcon, str (path, resource, URL, or SVG), or None."""
        # ////// HANDLE NONE
        if value is None:
            self._hover_icon = None
        # ////// HANDLE QICON
        elif isinstance(value, QIcon):
            self._hover_icon = value
        # ////// HANDLE STRING (PATH, URL, SVG)
        elif isinstance(value, str):
            # ////// HANDLE URL
            if value.startswith("http://") or value.startswith("https://"):
                print(f"Loading icon from URL: {value}")
                try:
                    response = requests.get(value, timeout=5)
                    response.raise_for_status()
                    if "image" not in response.headers.get("Content-Type", ""):
                        raise ValueError("URL does not point to an image file.")
                    image_data = response.content
                    # ////// HANDLE SVG FROM URL
                    if value.lower().endswith(".svg"):
                        from PySide6.QtSvg import QSvgRenderer
                        from PySide6.QtCore import QByteArray

                        renderer = QSvgRenderer(QByteArray(image_data))
                        pixmap = QPixmap(self._icon_size)
                        pixmap.fill(Qt.transparent)
                        painter = QPainter(pixmap)
                        renderer.render(painter)
                        painter.end()
                        self._hover_icon = QIcon(pixmap)
                    # ////// HANDLE RASTER IMAGE FROM URL
                    else:
                        pixmap = QPixmap()
                        if not pixmap.loadFromData(image_data):
                            raise ValueError(
                                "Failed to load image data from URL (unsupported format or corrupt image)."
                            )
                        self._hover_icon = QIcon(pixmap)
                except Exception as e:
                    raise ValueError(f"Failed to load icon from URL: {e}")
            # ////// HANDLE LOCAL SVG
            elif value.lower().endswith(".svg"):
                try:
                    from PySide6.QtSvg import QSvgRenderer
                    from PySide6.QtCore import QFile

                    file = QFile(value)
                    if not file.open(QFile.ReadOnly):
                        raise ValueError(f"Cannot open SVG file: {value}")
                    svg_data = file.readAll()
                    file.close()
                    renderer = QSvgRenderer(svg_data)
                    pixmap = QPixmap(self._icon_size)
                    pixmap.fill(Qt.transparent)
                    painter = QPainter(pixmap)
                    renderer.render(painter)
                    painter.end()
                    self._hover_icon = QIcon(pixmap)
                except Exception as e:
                    raise ValueError(f"Failed to load SVG icon: {e}")
            # ////// HANDLE LOCAL/RESOURCE RASTER IMAGE
            else:
                icon = QIcon(value)
                if icon.isNull():
                    raise ValueError(f"Invalid icon path: {value}")
                self._hover_icon = icon
        # ////// HANDLE INVALID TYPE
        else:
            raise TypeError("hover_icon must be a QIcon, a path string, or None.")
        # ////// UPDATE STYLE

        self._update_padding_style()
        self.update()

    @property
    def icon_size(self) -> QSize:
        """Get or set the size of the hover icon."""
        return self._icon_size

    @icon_size.setter
    def icon_size(self, value: Union[QSize, Tuple[int, int]]) -> None:
        """Set the size of the hover icon."""
        if isinstance(value, QSize):
            self._icon_size = value
        elif isinstance(value, (tuple, list)) and len(value) == 2:
            self._icon_size = QSize(*value)
        else:
            raise TypeError(
                "icon_size must be a QSize or a tuple/list of two integers."
            )
        self._update_padding_style()
        self.update()

    @property
    def icon_color(self) -> Optional[Union[QColor, str]]:
        """Get or set the color overlay of the hover icon (QColor, str, or None)."""
        return self._icon_color

    @icon_color.setter
    def icon_color(self, value: Optional[Union[QColor, str]]) -> None:
        """Set the color overlay of the hover icon."""
        self._icon_color = value
        self.update()

    @property
    def icon_padding(self) -> int:
        """Get or set the right padding for the icon."""
        return self._icon_padding

    @icon_padding.setter
    def icon_padding(self, value: int) -> None:
        """Set the right padding for the icon."""
        self._icon_padding = int(value)
        self._update_padding_style()
        self.update()

    @property
    def icon_enabled(self) -> bool:
        """Enable or disable the hover icon."""
        return self._icon_enabled

    @icon_enabled.setter
    def icon_enabled(self, value: bool) -> None:
        """Set whether the icon is enabled."""
        self._icon_enabled = bool(value)
        self._update_padding_style()
        self.update()

    # UTILITY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def clear_icon(self) -> None:
        """Remove the hover icon."""
        # ////// CLEAR ICON
        self._hover_icon = None
        self._update_padding_style()
        self.update()

    def _update_padding_style(self) -> None:
        """Update the padding style based on icon state."""
        padding = (
            self._icon_size.width() + self._icon_padding
            if self._hover_icon and self._icon_enabled
            else 0
        )
        self.setStyleSheet(f"padding-right: {padding}px;")

    # EVENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse movement events."""
        if not self._icon_enabled or not self._hover_icon:
            super().mouseMoveEvent(event)
            return

        # ////// CALCULATE ICON RECTANGLE (RIGHT SIDE)
        icon_x = self.width() - self._icon_size.width() - 4
        icon_y = (self.height() - self._icon_size.height()) // 2
        icon_rect = QRect(
            icon_x, icon_y, self._icon_size.width(), self._icon_size.height()
        )

        # ////// CHECK HOVER STATE
        if icon_rect.contains(event.pos()):
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

        super().mouseMoveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press events."""
        if not self._icon_enabled or not self._hover_icon:
            super().mousePressEvent(event)
            return

        # ////// CALCULATE ICON RECTANGLE (RIGHT SIDE)
        icon_x = self.width() - self._icon_size.width() - 4
        icon_y = (self.height() - self._icon_size.height()) // 2
        icon_rect = QRect(
            icon_x, icon_y, self._icon_size.width(), self._icon_size.height()
        )

        # ////// CHECK CLICK ON ICON
        if (
            icon_rect.contains(event.position().toPoint())
            and event.button() == Qt.LeftButton
        ):
            self.hoverIconClicked.emit()
        else:
            super().mousePressEvent(event)

    def enterEvent(self, event: QEnterEvent) -> None:
        """Handle enter events."""
        self._show_hover_icon = True
        self.update()  # Demande de redessiner le widget
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        """Handle leave events."""
        self._show_hover_icon = False
        self.setCursor(Qt.ArrowCursor)
        self.update()
        super().leaveEvent(event)

    # UI FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paint the widget."""
        super().paintEvent(event)

        # ////// DRAW HOVER ICON IF NEEDED
        if self._show_hover_icon and self._hover_icon and self._icon_enabled:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setOpacity(self._opacity)

            # ////// CALCULATE ICON POSITION (RIGHT SIDE)
            icon_x = self.width() - self._icon_size.width() - 4
            icon_y = (self.height() - self._icon_size.height()) // 2
            icon_rect = QRect(
                icon_x, icon_y, self._icon_size.width(), self._icon_size.height()
            )

            # ////// GET ICON PIXMAP
            icon_pixmap = self._hover_icon.pixmap(self._icon_size)

            # ////// APPLY COLOR OVERLAY IF SPECIFIED
            if self._icon_color and not icon_pixmap.isNull():
                colored_pixmap = QPixmap(icon_pixmap.size())
                colored_pixmap.fill(Qt.transparent)
                overlay_painter = QPainter(colored_pixmap)
                overlay_painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                overlay_painter.fillRect(
                    colored_pixmap.rect(), QColor(self._icon_color)
                )
                overlay_painter.setCompositionMode(
                    QPainter.CompositionMode_DestinationIn
                )
                overlay_painter.drawPixmap(0, 0, icon_pixmap)
                overlay_painter.end()
                painter.drawPixmap(icon_rect, colored_pixmap)
            elif not icon_pixmap.isNull():
                painter.drawPixmap(icon_rect, icon_pixmap)

    # OVERRIDE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handle resize events."""
        super().resizeEvent(event)
        self.update()

    def minimumSizeHint(self) -> QSize:
        """Get the minimum size hint for the widget."""
        base = super().minimumSizeHint()
        min_width = self._min_width if self._min_width is not None else base.width()
        return QSize(min_width, base.height())

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refresh_style(self) -> None:
        """Refresh the widget's style (useful after dynamic stylesheet changes)."""
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
