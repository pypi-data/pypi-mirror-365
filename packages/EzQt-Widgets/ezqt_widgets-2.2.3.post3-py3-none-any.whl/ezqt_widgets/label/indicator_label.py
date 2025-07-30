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
)
from PySide6.QtWidgets import (
    QHBoxLayout,
    QSizePolicy,
    QFrame,
    QLabel,
)
from PySide6.QtGui import (
    QFont,
)

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////

# ////// TYPE HINTS IMPROVEMENTS FOR PYSIDE6 6.9.1
from typing import Optional, Dict

# UTILITY FUNCTIONS
# ///////////////////////////////////////////////////////////////

# CLASS
# ///////////////////////////////////////////////////////////////


class IndicatorLabel(QFrame):
    """
    IndicatorLabel is a dynamic status indicator widget based on QFrame, designed for displaying a status label and a colored LED in Qt applications.

    This widget encapsulates a QLabel for the status text and a QLabel for the LED, both arranged horizontally. The possible states are defined in a configurable dictionary (status_map), allowing for flexible text, color, and state property assignment.

    Features:
        - Dynamic states defined via a status_map dictionary (text, state, color)
        - Property-based access to the current status (status)
        - Emits a statusChanged(str) signal when the status changes
        - Allows custom status sets and colors for various use cases
        - Suitable for online/offline indicators, service status, etc.

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget (default: None).
    status_map : dict, optional
        Dictionary defining possible states. Each key is a state name, and each value is a dict with keys:
            - text (str): The label to display
            - state (str): The value set as a Qt property for styling
            - color (str): The LED color (any valid CSS color)
        Example:
            {
                "neutral": {"text": "En attente", "state": "none", "color": "#A0A0A0"},
                "online": {"text": "En ligne", "state": "ok", "color": "#4CAF50"},
                ...
            }
    initial_status : str, optional
        The initial status key to use (default: "neutral").
    *args, **kwargs :
        Additional arguments passed to QFrame.

    Properties
    ----------
    status : str
        Get or set the current status key.

    Signals
    -------
    statusChanged(str)
        Emitted when the status changes.
    """

    statusChanged = Signal(str)

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(
        self,
        parent=None,
        status_map: Optional[Dict[str, Dict[str, str]]] = None,
        initial_status: str = "neutral",
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)

        # ////// SET TYPE PROPERTY FOR QSS STYLING
        self.setProperty("type", "IndicatorLabel")

        # ////// DEFAULT STATUS MAP
        self._status_map: Dict[str, Dict[str, str]] = status_map or {
            "neutral": {"text": "En attente", "state": "none", "color": "#A0A0A0"},
            "online": {"text": "En ligne", "state": "ok", "color": "#4CAF50"},
            "partial": {
                "text": "Services perturbés",
                "state": "partiel",
                "color": "#FFC107",
            },
            "offline": {"text": "Hors ligne", "state": "ko", "color": "#F44336"},
        }

        # ////// STATE VARIABLES
        self._current_status: str = ""  # Initialize empty to force first update
        self._status_label: Optional[QLabel] = None
        self._led_label: Optional[QLabel] = None

        # ////// SETUP WIDGET
        self._setup_widget()

        # ////// SET INITIAL STATUS
        self.status = initial_status

    def _setup_widget(self) -> None:
        """Setup the widget properties and layout."""
        # ////// SETUP FRAME
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Raised)
        self.setContentsMargins(4, 2, 4, 2)
        self.setFixedHeight(24)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        # ////// CREATE LAYOUT
        self._layout = QHBoxLayout(self)
        self._layout.setObjectName("status_HLayout")
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(8)

        # ////// CREATE STATUS LABEL
        self._status_label = QLabel()
        self._status_label.setObjectName("status_label")
        self._status_label.setFont(QFont("Segoe UI", 10))
        self._status_label.setLineWidth(0)
        self._status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # ////// CREATE LED LABEL
        self._led_label = QLabel()
        self._led_label.setObjectName("status_led")
        self._led_label.setFixedSize(QSize(13, 16))
        self._led_label.setFont(QFont("Segoe UI", 10))
        self._led_label.setLineWidth(0)
        self._led_label.setAlignment(Qt.AlignCenter)

        # ////// ADD WIDGETS TO LAYOUT
        self._layout.addWidget(self._status_label, 0, Qt.AlignmentFlag.AlignTop)
        self._layout.addWidget(self._led_label, 0, Qt.AlignmentFlag.AlignTop)

    # PROPERTIES
    # ///////////////////////////////////////////////////////////////

    @property
    def status(self) -> str:
        """Get the current status key."""
        return self._current_status

    @status.setter
    def status(self, value: str) -> None:
        """Set the current status key."""
        self.set_status(value)

    # UTILITY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def set_status(self, status: str) -> None:
        """Set the current status and update the display."""
        if status not in self._status_map:
            # ////// RAISE ERROR FOR UNKNOWN STATUS (LIKE OLD VERSION)
            raise ValueError(f"Unknown status: {status}")

        if status != self._current_status:
            self._current_status = status
            self._update_display()
            self.statusChanged.emit(self._current_status)

    def _update_display(self) -> None:
        """Update the display based on current status."""
        if not self._status_label or not self._led_label:
            return

        # ////// GET STATUS INFO
        status_info = self._status_map.get(self._current_status, {})
        text = status_info.get("text", "Inconnu")
        state = status_info.get("state", "none")
        color = status_info.get("color", "#A0A0A0")

        # ////// UPDATE STATUS LABEL
        self._status_label.setText(text)

        # ////// UPDATE LED COLOR (LIKE OLD VERSION)
        self._led_label.setStyleSheet(
            f"""
            background-color: {color};
            border: 2px solid rgb(66, 66, 66);
            border-radius: 6px;
            margin-top: 3px;
            """
        )

        # ////// SET STATE PROPERTY FOR STYLING
        self.setProperty("state", state)
        self.style().unpolish(self)
        self.style().polish(self)

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refresh_style(self) -> None:
        """Refresh the widget style."""
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
