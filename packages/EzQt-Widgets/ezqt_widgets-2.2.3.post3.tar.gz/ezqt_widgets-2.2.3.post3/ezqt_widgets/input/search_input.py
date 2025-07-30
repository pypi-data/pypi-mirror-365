# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

# IMPORT BASE
# ///////////////////////////////////////////////////////////////

# IMPORT SPECS
# ///////////////////////////////////////////////////////////////
from PySide6.QtCore import (
    Signal,
    Qt,
)
from PySide6.QtGui import (
    QIcon,
    QKeyEvent,
)
from PySide6.QtWidgets import (
    QLineEdit,
)

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////

# ////// TYPE HINTS IMPROVEMENTS FOR PYSIDE6 6.9.1
from typing import Optional, Union, List

# UTILITY FUNCTIONS
# ///////////////////////////////////////////////////////////////

# CLASS
# ///////////////////////////////////////////////////////////////


class SearchInput(QLineEdit):
    """
    QLineEdit subclass for search input with integrated history and optional search icon.

    Features:
        - Maintains a history of submitted searches
        - Navigate history with up/down arrows
        - Emits a searchSubmitted(str) signal on validation (Enter)
        - Optional search icon (left or right)
        - Optional clear button

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget (default: None).
    max_history : int, optional
        Maximum number of history entries to keep (default: 20).
    search_icon : QIcon or str, optional
        Icon to display as search icon (default: None).
    icon_position : str, optional
        'left' or 'right' (default: 'left').
    clear_button : bool, optional
        Whether to show a clear button (default: True).

    Properties
    ----------
    search_icon : QIcon
        Get or set the search icon.
    icon_position : str
        Get or set the icon position ('left' or 'right').
    clear_button : bool
        Get or set whether the clear button is shown.
    max_history : int
        Get or set the maximum history size.

    Signals
    -------
    searchSubmitted(str)
        Emitted when a search is submitted (Enter key).
    """

    searchSubmitted = Signal(str)

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(
        self,
        parent=None,
        max_history: int = 20,
        search_icon: Optional[Union[QIcon, str]] = None,
        icon_position: str = "left",
        clear_button: bool = True,
        *args,
        **kwargs,
    ):
        super().__init__(parent, *args, **kwargs)

        # ////// INITIALIZE PROPERTIES
        self._search_icon: Optional[QIcon] = None
        self._icon_position: str = icon_position
        self._clear_button: bool = clear_button
        self._history: List[str] = []
        self._history_index: int = -1
        self._max_history: int = max_history
        self._current_text: str = ""

        # ////// SETUP UI
        self._setup_ui()

        # ////// SET ICON
        if search_icon:
            self.search_icon = search_icon

    def _setup_ui(self) -> None:
        """Setup the user interface components."""
        self.setPlaceholderText("Search...")
        self.setClearButtonEnabled(self._clear_button)

    # PROPERTIES
    # ///////////////////////////////////////////////////////////////

    @property
    def search_icon(self) -> Optional[QIcon]:
        """Get the search icon."""
        return self._search_icon

    @search_icon.setter
    def search_icon(self, value: Optional[Union[QIcon, str]]) -> None:
        """Set the search icon."""
        if isinstance(value, str):
            # ////// LOAD ICON FROM PATH
            self._search_icon = QIcon(value)
        else:
            self._search_icon = value

        # ////// UPDATE DISPLAY
        if self._search_icon:
            self.setStyleSheet(
                f"""
                QLineEdit {{
                    padding-{self._icon_position}: 20px;
                }}
            """
            )
        else:
            self.setStyleSheet("")

    @property
    def icon_position(self) -> str:
        """Get the icon position."""
        return self._icon_position

    @icon_position.setter
    def icon_position(self, value: str) -> None:
        """Set the icon position."""
        if value in ["left", "right"]:
            self._icon_position = value
            # ////// UPDATE ICON DISPLAY
            if self._search_icon:
                self.search_icon = self._search_icon

    @property
    def clear_button(self) -> bool:
        """Get whether the clear button is shown."""
        return self._clear_button

    @clear_button.setter
    def clear_button(self, value: bool) -> None:
        """Set whether the clear button is shown."""
        self._clear_button = bool(value)
        self.setClearButtonEnabled(self._clear_button)

    @property
    def max_history(self) -> int:
        """Get the maximum history size."""
        return self._max_history

    @max_history.setter
    def max_history(self, value: int) -> None:
        """Set the maximum history size."""
        self._max_history = max(1, int(value))
        self._trim_history()

    # UTILITY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def add_to_history(self, text: str) -> None:
        """Add a search term to history."""
        if not text.strip():
            return

        # ////// REMOVE IF ALREADY EXISTS
        if text in self._history:
            self._history.remove(text)

        # ////// ADD TO BEGINNING
        self._history.insert(0, text)
        self._trim_history()
        self._history_index = -1

    def _trim_history(self) -> None:
        """Trim history to maximum size."""
        while len(self._history) > self._max_history:
            self._history.pop()

    def get_history(self) -> List[str]:
        """Get the search history."""
        return self._history.copy()

    def clear_history(self) -> None:
        """Clear the search history."""
        self._history.clear()
        self._history_index = -1

    def set_history(self, history_list: List[str]) -> None:
        """Set the search history."""
        self._history = [
            str(item).strip() for item in history_list if str(item).strip()
        ]
        self._trim_history()
        self._history_index = -1

    # EVENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press events."""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # ////// SUBMIT SEARCH
            text = self.text().strip()
            if text:
                self.add_to_history(text)
                self.searchSubmitted.emit(text)
        elif event.key() == Qt.Key_Up:
            # ////// NAVIGATE HISTORY UP
            if self._history:
                if self._history_index < len(self._history) - 1:
                    self._history_index += 1
                    self.setText(self._history[self._history_index])
                event.accept()
                return
        elif event.key() == Qt.Key_Down:
            # ////// NAVIGATE HISTORY DOWN
            if self._history_index > 0:
                self._history_index -= 1
                self.setText(self._history[self._history_index])
                event.accept()
                return
            elif self._history_index == 0:
                self._history_index = -1
                self.setText(self._current_text)
                event.accept()
                return

        # ////// STORE CURRENT TEXT FOR HISTORY NAVIGATION
        if event.key() not in [Qt.Key_Up, Qt.Key_Down]:
            self._current_text = self.text()

        super().keyPressEvent(event)

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refresh_style(self) -> None:
        """Refresh the widget style."""
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
