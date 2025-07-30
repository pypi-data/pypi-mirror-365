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
    QDate,
)
from PySide6.QtGui import (
    QIcon,
    QPixmap,
    QPainter,
    QColor,
    QMouseEvent,
)
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QToolButton,
    QSizePolicy,
    QCalendarWidget,
    QDialog,
    QVBoxLayout,
    QPushButton,
)

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////

# ////// TYPE HINTS IMPROVEMENTS FOR PYSIDE6 6.9.1
from typing import Optional, Union, Tuple

# UTILITY FUNCTIONS
# ///////////////////////////////////////////////////////////////


def format_date(date: QDate, format_str: str = "dd/MM/yyyy") -> str:
    """
    Format a QDate object to string.

    Parameters
    ----------
    date : QDate
        The date to format.
    format_str : str, optional
        Format string (default: "dd/MM/yyyy").

    Returns
    -------
    str
        Formatted date string.
    """
    if not date.isValid():
        return ""
    return date.toString(format_str)


def parse_date(date_str: str, format_str: str = "dd/MM/yyyy") -> QDate:
    """
    Parse a date string to QDate object.

    Parameters
    ----------
    date_str : str
        The date string to parse.
    format_str : str, optional
        Format string (default: "dd/MM/yyyy").

    Returns
    -------
    QDate
        Parsed QDate object or invalid QDate if parsing fails.
    """
    return QDate.fromString(date_str, format_str)


def get_calendar_icon() -> QIcon:
    """Get a default calendar icon."""
    # Create a simple calendar icon
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setPen(QColor("#666666"))
    painter.setBrush(QColor("#f0f0f0"))
    painter.drawRect(0, 0, 15, 15)
    painter.setPen(QColor("#333333"))
    painter.drawText(2, 2, 12, 12, Qt.AlignCenter, "📅")
    painter.end()
    return QIcon(pixmap)


# CLASS
# ///////////////////////////////////////////////////////////////


class DatePickerDialog(QDialog):
    """
    Dialog for date selection with calendar widget.

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget (default: None).
    current_date : QDate, optional
        The current selected date (default: None).
    """

    def __init__(self, parent=None, current_date: Optional[QDate] = None):
        super().__init__(parent)

        # ////// INITIALIZE PROPERTIES
        self._selected_date: Optional[QDate] = current_date

        # ////// SETUP UI
        self._setup_ui()

        # ////// SET CURRENT DATE
        if current_date and current_date.isValid():
            self._calendar.setSelectedDate(current_date)

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        self.setWindowTitle("Sélectionner une date")
        self.setModal(True)
        self.setFixedSize(300, 250)

        # ////// CREATE LAYOUT
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # ////// CREATE CALENDAR
        self._calendar = QCalendarWidget(self)
        self._calendar.clicked.connect(self._on_date_selected)
        layout.addWidget(self._calendar)

        # ////// CREATE BUTTONS
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        ok_button = QPushButton("OK", self)
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Annuler", self)
        cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)

        # ////// CONNECTIONS
        self._calendar.activated.connect(self.accept)

    def _on_date_selected(self, date: QDate) -> None:
        """Handle date selection from calendar."""
        self._selected_date = date

    def selected_date(self) -> Optional[QDate]:
        """Get the selected date."""
        return self._selected_date


class DateButton(QToolButton):
    """
    Button widget for date selection with integrated calendar.

    Features:
        - Displays current selected date
        - Opens calendar dialog on click
        - Configurable date format
        - Placeholder text when no date selected
        - Calendar icon with customizable appearance
        - Date validation and parsing

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget (default: None).
    date : QDate or str, optional
        Initial date (QDate, date string, or None for current date).
    date_format : str, optional
        Format for displaying the date (default: "dd/MM/yyyy").
    placeholder : str, optional
        Text to display when no date is selected (default: "Sélectionner une date").
    show_calendar_icon : bool, optional
        Whether to show calendar icon (default: True).
    icon_size : QSize or tuple, optional
        Size of the calendar icon (default: QSize(16, 16)).
    min_width : int, optional
        Minimum width of the button (default: None, auto-calculated).
    min_height : int, optional
        Minimum height of the button (default: None, auto-calculated).
    *args, **kwargs :
        Additional arguments passed to QToolButton.

    Properties
    ----------
    date : QDate
        Get or set the selected date.
    date_string : str
        Get or set the date as formatted string.
    date_format : str
        Get or set the date format.
    placeholder : str
        Get or set the placeholder text.
    show_calendar_icon : bool
        Get or set calendar icon visibility.
    icon_size : QSize
        Get or set the icon size.
    min_width : int
        Get or set the minimum width.
    min_height : int
        Get or set the minimum height.

    Signals
    -------
    dateChanged(QDate)
        Emitted when the date changes.
    dateSelected(QDate)
        Emitted when a date is selected from calendar.
    """

    dateChanged = Signal(QDate)
    dateSelected = Signal(QDate)

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(
        self,
        parent=None,
        date: Optional[Union[QDate, str]] = None,
        date_format: str = "dd/MM/yyyy",
        placeholder: str = "Sélectionner une date",
        show_calendar_icon: bool = True,
        icon_size: Union[QSize, Tuple[int, int]] = QSize(16, 16),
        min_width: Optional[int] = None,
        min_height: Optional[int] = None,
        *args,
        **kwargs,
    ):
        super().__init__(parent, *args, **kwargs)
        self.setProperty("type", "DateButton")

        # ////// INITIALIZE VARIABLES
        self._date_format: str = date_format
        self._placeholder: str = placeholder
        self._show_calendar_icon: bool = show_calendar_icon
        self._icon_size: QSize = (
            QSize(*icon_size)
            if isinstance(icon_size, (tuple, list))
            else QSize(icon_size)
        )
        self._min_width: Optional[int] = min_width
        self._min_height: Optional[int] = min_height
        self._current_date: QDate = QDate()

        # ////// SETUP UI COMPONENTS
        self.date_label = QLabel()
        self.icon_label = QLabel()

        # ////// CONFIGURE LABELS
        self.date_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.date_label.setStyleSheet("background-color: transparent;")

        # ////// SETUP LAYOUT
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.date_label)
        layout.addStretch()  # ////// PUSH ICON TO THE RIGHT
        layout.addWidget(self.icon_label)

        # ////// CONFIGURE SIZE POLICY
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # ////// SET INITIAL VALUES
        if date:
            self.date = date
        else:
            self.date = QDate.currentDate()

        self.show_calendar_icon = show_calendar_icon
        self._update_display()

    # PROPERTY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    @property
    def date(self) -> QDate:
        """Get or set the selected date."""
        return self._current_date

    @date.setter
    def date(self, value: Optional[Union[QDate, str]]) -> None:
        """Set the date from QDate, string, or None."""
        if isinstance(value, str):
            new_date = parse_date(value, self._date_format)
        elif isinstance(value, QDate):
            new_date = value
        elif value is None:
            new_date = QDate()
        else:
            return

        if new_date != self._current_date:
            self._current_date = new_date
            self._update_display()
            self.dateChanged.emit(self._current_date)

    @property
    def date_string(self) -> str:
        """Get or set the date as formatted string."""
        return format_date(self._current_date, self._date_format)

    @date_string.setter
    def date_string(self, value: str) -> None:
        """Set the date from a formatted string."""
        self.date = value

    @property
    def date_format(self) -> str:
        """Get or set the date format."""
        return self._date_format

    @date_format.setter
    def date_format(self, value: str) -> None:
        """Set the date format."""
        self._date_format = str(value)
        self._update_display()

    @property
    def placeholder(self) -> str:
        """Get or set the placeholder text."""
        return self._placeholder

    @placeholder.setter
    def placeholder(self, value: str) -> None:
        """Set the placeholder text."""
        self._placeholder = str(value)
        self._update_display()

    @property
    def show_calendar_icon(self) -> bool:
        """Get or set calendar icon visibility."""
        return self._show_calendar_icon

    @show_calendar_icon.setter
    def show_calendar_icon(self, value: bool) -> None:
        """Set calendar icon visibility."""
        self._show_calendar_icon = bool(value)
        if self._show_calendar_icon:
            self.icon_label.show()
            self.icon_label.setPixmap(get_calendar_icon().pixmap(self._icon_size))
            self.icon_label.setFixedSize(self._icon_size)
        else:
            self.icon_label.hide()

    @property
    def icon_size(self) -> QSize:
        """Get or set the icon size."""
        return self._icon_size

    @icon_size.setter
    def icon_size(self, value: Union[QSize, Tuple[int, int]]) -> None:
        """Set the icon size."""
        self._icon_size = (
            QSize(*value) if isinstance(value, (tuple, list)) else QSize(value)
        )
        if self._show_calendar_icon:
            self.icon_label.setPixmap(get_calendar_icon().pixmap(self._icon_size))
            self.icon_label.setFixedSize(self._icon_size)

    @property
    def min_width(self) -> Optional[int]:
        """Get or set the minimum width of the button."""
        return self._min_width

    @min_width.setter
    def min_width(self, value: Optional[int]) -> None:
        """Set the minimum width of the button."""
        self._min_width = value
        self.updateGeometry()

    @property
    def min_height(self) -> Optional[int]:
        """Get or set the minimum height of the button."""
        return self._min_height

    @min_height.setter
    def min_height(self, value: Optional[int]) -> None:
        """Set the minimum height of the button."""
        self._min_height = value
        self.updateGeometry()

    # UTILITY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def clear_date(self) -> None:
        """Clear the selected date."""
        self.date = None

    def set_today(self) -> None:
        """Set the date to today."""
        self.date = QDate.currentDate()

    def open_calendar(self) -> None:
        """Open the calendar dialog."""
        dialog = DatePickerDialog(self, self._current_date)
        if dialog.exec() == QDialog.Accepted:
            selected_date = dialog.selected_date()
            if selected_date and selected_date.isValid():
                self.date = selected_date
                self.dateSelected.emit(selected_date)

    def _update_display(self) -> None:
        """Update the display text."""
        if self._current_date.isValid():
            display_text = format_date(self._current_date, self._date_format)
        else:
            display_text = self._placeholder

        self.date_label.setText(display_text)

    # EVENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            self.open_calendar()
        super().mousePressEvent(event)

    # OVERRIDE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def sizeHint(self) -> QSize:
        """Get the recommended size for the button."""
        return QSize(150, 30)

    def minimumSizeHint(self) -> QSize:
        """Get the minimum size hint for the button."""
        # ////// CALCULATE BASE SIZE
        base_size = super().minimumSizeHint()

        # ////// CALCULATE TEXT SPACE
        text_width = self.date_label.fontMetrics().horizontalAdvance(
            self.date_string if self._current_date.isValid() else self._placeholder
        )

        # ////// CALCULATE ICON SPACE
        icon_width = self._icon_size.width() if self._show_calendar_icon else 0

        # ////// CALCULATE TOTAL WIDTH
        total_width = text_width + icon_width + 16 + 8  # margins + spacing

        # ////// APPLY MINIMUM CONSTRAINTS
        min_width = self._min_width if self._min_width is not None else total_width
        min_height = (
            self._min_height
            if self._min_height is not None
            else max(base_size.height(), 30)
        )

        return QSize(max(min_width, total_width), min_height)

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refresh_style(self) -> None:
        """Refresh the widget's style (useful after dynamic stylesheet changes)."""
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
