# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

# IMPORT BASE
# ///////////////////////////////////////////////////////////////

# IMPORT SPECS
# ///////////////////////////////////////////////////////////////
from PySide6.QtCore import (
    Qt,
    QStringListModel,
)
from PySide6.QtWidgets import (
    QLineEdit,
    QCompleter,
)

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////

# ////// TYPE HINTS IMPROVEMENTS FOR PYSIDE6 6.9.1
from typing import Optional, List

# UTILITY FUNCTIONS
# ///////////////////////////////////////////////////////////////

# CLASS
# ///////////////////////////////////////////////////////////////


class AutoCompleteInput(QLineEdit):
    """
    QLineEdit subclass with autocompletion support.
    You can provide a list of suggestions (strings) to be used for autocompletion.

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget (default: None).
    suggestions : List[str], optional
        List of strings to use for autocompletion (default: empty list).
    case_sensitive : bool, optional
        Whether the autocompletion is case sensitive (default: False).
    filter_mode : Qt.MatchFlag, optional
        Filter mode for completion (default: Qt.MatchContains).
    completion_mode : QCompleter.CompletionMode, optional
        Completion mode (default: QCompleter.PopupCompletion).
    *args, **kwargs :
        Additional arguments passed to QLineEdit.

    Properties
    ----------
    suggestions : List[str]
        Get or set the list of suggestions for autocompletion.
    case_sensitive : bool
        Get or set whether autocompletion is case sensitive.
    filter_mode : Qt.MatchFlag
        Get or set the filter mode for completion.
    completion_mode : QCompleter.CompletionMode
        Get or set the completion mode.
    """

    def __init__(
        self,
        parent=None,
        suggestions: Optional[List[str]] = None,
        case_sensitive: bool = False,
        filter_mode: Qt.MatchFlag = Qt.MatchContains,
        completion_mode: QCompleter.CompletionMode = QCompleter.PopupCompletion,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)

        # ////// INITIALIZE PROPERTIES
        self._suggestions: List[str] = suggestions or []
        self._case_sensitive: bool = case_sensitive
        self._filter_mode: Qt.MatchFlag = filter_mode
        self._completion_mode: QCompleter.CompletionMode = completion_mode

        # ////// SETUP COMPLETER
        self._setup_completer()

    def _setup_completer(self) -> None:
        """Setup the completer with current settings."""
        self._completer = QCompleter(self)
        self._model = QStringListModel(self._suggestions, self)

        # ////// CONFIGURE COMPLETER
        self._completer.setModel(self._model)
        self._completer.setCaseSensitivity(
            Qt.CaseSensitive if self._case_sensitive else Qt.CaseInsensitive
        )
        self._completer.setFilterMode(self._filter_mode)
        self._completer.setCompletionMode(self._completion_mode)
        self.setCompleter(self._completer)

    # PROPERTIES
    # ///////////////////////////////////////////////////////////////

    @property
    def suggestions(self) -> List[str]:
        """Get the list of suggestions."""
        return self._suggestions.copy()

    @suggestions.setter
    def suggestions(self, value: List[str]) -> None:
        """Set the list of suggestions."""
        self._suggestions = value or []
        self._model.setStringList(self._suggestions)

    @property
    def case_sensitive(self) -> bool:
        """Get whether autocompletion is case sensitive."""
        return self._case_sensitive

    @case_sensitive.setter
    def case_sensitive(self, value: bool) -> None:
        """Set whether autocompletion is case sensitive."""
        self._case_sensitive = bool(value)
        self._completer.setCaseSensitivity(
            Qt.CaseSensitive if self._case_sensitive else Qt.CaseInsensitive
        )

    @property
    def filter_mode(self) -> Qt.MatchFlag:
        """Get the filter mode for completion."""
        return self._filter_mode

    @filter_mode.setter
    def filter_mode(self, value: Qt.MatchFlag) -> None:
        """Set the filter mode for completion."""
        self._filter_mode = value
        self._completer.setFilterMode(self._filter_mode)

    @property
    def completion_mode(self) -> QCompleter.CompletionMode:
        """Get the completion mode."""
        return self._completion_mode

    @completion_mode.setter
    def completion_mode(self, value: QCompleter.CompletionMode) -> None:
        """Set the completion mode."""
        self._completion_mode = value
        self._completer.setCompletionMode(self._completion_mode)

    # UTILITY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def add_suggestion(self, suggestion: str) -> None:
        """Add a suggestion to the list."""
        if suggestion and suggestion not in self._suggestions:
            self._suggestions.append(suggestion)
            self._model.setStringList(self._suggestions)

    def remove_suggestion(self, suggestion: str) -> None:
        """Remove a suggestion from the list."""
        if suggestion in self._suggestions:
            self._suggestions.remove(suggestion)
            self._model.setStringList(self._suggestions)

    def clear_suggestions(self) -> None:
        """Clear all suggestions."""
        self._suggestions.clear()
        self._model.setStringList(self._suggestions)

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refresh_style(self) -> None:
        """Refresh the widget's style (useful after dynamic stylesheet changes)."""
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
