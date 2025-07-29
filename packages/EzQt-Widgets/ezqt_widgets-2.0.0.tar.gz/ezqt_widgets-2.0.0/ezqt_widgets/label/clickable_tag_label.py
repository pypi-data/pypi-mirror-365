# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

# IMPORT BASE
# ///////////////////////////////////////////////////////////////

# IMPORT SPECS
# ///////////////////////////////////////////////////////////////
from PySide6.QtCore import (
    Signal,
    Qt,
    QSize,
)
from PySide6.QtGui import (
    QMouseEvent,
    QKeyEvent,
    QFont,
)
from PySide6.QtWidgets import (
    QHBoxLayout,
    QSizePolicy,
    QFrame,
    QLabel,
)

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////

# ////// TYPE HINTS IMPROVEMENTS FOR PYSIDE6 6.9.1
from typing import Optional

# UTILITY FUNCTIONS
# ///////////////////////////////////////////////////////////////

# CLASS
# ///////////////////////////////////////////////////////////////


class ClickableTagLabel(QFrame):
    """
    Tag-like clickable label with toggleable state.

    Features:
        - Clickable tag with enabled/disabled state
        - Emits signals on click and state change
        - Customizable text, font, min width/height
        - Customizable status color (traditional name or hex)
        - QSS-friendly (type/class/status properties)
        - Automatic minimum size calculation
        - Keyboard focus and accessibility

    Parameters
    ----------
    name : str, optional
        Text to display in the tag (default: "").
    enabled : bool, optional
        Initial state (default: False).
    status_color : str, optional
        Color when selected (default: "#0078d4").
    min_width : int, optional
        Minimum width (default: None, auto-calculated).
    min_height : int, optional
        Minimum height (default: None, auto-calculated).
    parent : QWidget, optional
        Parent widget (default: None).
    *args, **kwargs :
        Additional arguments passed to QFrame.

    Properties
    ----------
    name : str
        Get or set the tag text.
    enabled : bool
        Get or set the enabled state.
    status_color : str
        Get or set the status color.
    min_width : int
        Get or set the minimum width.
    min_height : int
        Get or set the minimum height.

    Signals
    -------
    clicked()
        Emitted when the tag is clicked.
    toggle_keyword(str)
        Emitted with the tag name when toggled.
    stateChanged(bool)
        Emitted when the enabled state changes.
    """

    clicked = Signal()
    toggle_keyword = Signal(str)
    stateChanged = Signal(bool)

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(
        self,
        name: str = "",
        enabled: bool = False,
        status_color: str = "#0078d4",
        min_width: Optional[int] = None,
        min_height: Optional[int] = None,
        parent=None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)

        # ////// SET PROPERTY TYPE FOR QSS
        self.setProperty("type", "ClickableTagLabel")

        # ////// INITIALIZE PROPERTIES
        self._name: str = name
        self._enabled: bool = enabled
        self._status_color: str = status_color
        self._min_width: Optional[int] = min_width
        self._min_height: Optional[int] = min_height

        # ////// SETUP UI
        self._setup_ui()
        self._update_display()

    def _setup_ui(self) -> None:
        """Setup the user interface components."""
        # ////// SETUP FRAME
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Raised)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setCursor(Qt.PointingHandCursor)
        self.setContentsMargins(4, 0, 4, 0)
        self.setFixedHeight(20)

        # ////// CREATE LAYOUT
        self._layout = QHBoxLayout(self)
        self._layout.setObjectName("status_HLayout")
        self._layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(12)

        # ////// CREATE LABEL
        self._label = QLabel()
        self._label.setObjectName("tag")
        self._label.setFont(QFont("Segoe UI", 8))
        self._label.setLineWidth(0)
        self._label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # ////// ADD LABEL TO LAYOUT
        self._layout.addWidget(self._label, 0, Qt.AlignmentFlag.AlignTop)

        # ////// SET MINIMUM SIZES
        if self._min_width:
            self.setMinimumWidth(self._min_width)
        if self._min_height:
            self.setMinimumHeight(self._min_height)

    def _update_display(self) -> None:
        """Update the display based on current state."""
        # ////// UPDATE LABEL TEXT
        self._label.setText(self._name)
        self.setObjectName(self._name)

        # ////// UPDATE QSS PROPERTIES
        if self._enabled:
            self.setProperty("status", "selected")
            self._label.setStyleSheet(
                f"color: {self._status_color}; background-color: transparent; border: none;"
            )
        else:
            self.setProperty("status", "unselected")
            self._label.setStyleSheet(
                "color: rgb(86, 86, 86); background-color: transparent; border: none;"
            )

        # ////// REFRESH STYLE
        self.refresh_style()
        self.adjustSize()

    # PROPERTIES
    # ///////////////////////////////////////////////////////////////

    @property
    def name(self) -> str:
        """Get the tag text."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the tag text."""
        self._name = str(value)
        self._update_display()
        self.updateGeometry()

    @property
    def enabled(self) -> bool:
        """Get the enabled state."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Set the enabled state."""
        if value != self._enabled:
            self._enabled = bool(value)
            self._update_display()
            self.stateChanged.emit(self._enabled)

    @property
    def status_color(self) -> str:
        """Get the status color."""
        return self._status_color

    @status_color.setter
    def status_color(self, value: str) -> None:
        """Set the status color."""
        self._status_color = str(value)
        if self._enabled:
            self._label.setStyleSheet(
                f"color: {value}; background-color: transparent; border: none;"
            )
            self.refresh_style()

    @property
    def min_width(self) -> Optional[int]:
        """Get the minimum width."""
        return self._min_width

    @min_width.setter
    def min_width(self, value: Optional[int]) -> None:
        """Set the minimum width."""
        self._min_width = value
        if value:
            self.setMinimumWidth(value)
        self.updateGeometry()

    @property
    def min_height(self) -> Optional[int]:
        """Get the minimum height."""
        return self._min_height

    @min_height.setter
    def min_height(self, value: Optional[int]) -> None:
        """Set the minimum height."""
        self._min_height = value
        if value:
            self.setMinimumHeight(value)
        self.updateGeometry()

    # EVENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.enabled = not self.enabled
            self.clicked.emit()
            self.toggle_keyword.emit(self._name)
        super().mousePressEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press events."""
        if event.key() in [Qt.Key_Space, Qt.Key_Return, Qt.Key_Enter]:
            self.enabled = not self.enabled
            self.clicked.emit()
            self.toggle_keyword.emit(self._name)
        else:
            super().keyPressEvent(event)

    # OVERRIDE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def sizeHint(self) -> QSize:
        """Return the recommended size for the widget."""
        return QSize(80, 24)

    def minimumSizeHint(self) -> QSize:
        """Return the minimum size for the widget."""
        # ////// CALCULATE MINIMUM SIZE
        font_metrics = self._label.fontMetrics()
        text_width = font_metrics.horizontalAdvance(self._name)
        min_width = self._min_width if self._min_width is not None else text_width + 16
        min_height = (
            self._min_height
            if self._min_height is not None
            else max(font_metrics.height() + 8, 20)
        )

        return QSize(min_width, min_height)

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refresh_style(self) -> None:
        """Refresh the widget style."""
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
