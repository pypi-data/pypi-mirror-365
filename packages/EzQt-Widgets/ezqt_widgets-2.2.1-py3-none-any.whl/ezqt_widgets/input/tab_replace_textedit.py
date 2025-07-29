# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

# IMPORT BASE
# ///////////////////////////////////////////////////////////////

# IMPORT SPECS
# ///////////////////////////////////////////////////////////////
from PySide6.QtCore import (
    Qt,
)
from PySide6.QtGui import (
    QKeySequence,
    QKeyEvent,
)
from PySide6.QtWidgets import (
    QApplication,
    QPlainTextEdit,
)

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////

# ////// TYPE HINTS IMPROVEMENTS FOR PYSIDE6 6.9.1

# UTILITY FUNCTIONS
# ///////////////////////////////////////////////////////////////

# CLASS
# ///////////////////////////////////////////////////////////////


class TabReplaceTextEdit(QPlainTextEdit):
    """
    QPlainTextEdit subclass that sanitizes pasted text by replacing tab characters according to the chosen mode
    and removing empty lines. Useful for pasting tabular data or ensuring clean input.

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget (default: None).
    tab_replacement : str, optional
        The string to replace tab characters with (default: "\n").
    sanitize_on_paste : bool, optional
        Whether to sanitize pasted text (default: True).
    remove_empty_lines : bool, optional
        Whether to remove empty lines during sanitization (default: True).
    preserve_whitespace : bool, optional
        Whether to preserve leading/trailing whitespace (default: False).
    *args, **kwargs :
        Additional arguments passed to QPlainTextEdit.

    Properties
    ----------
    tab_replacement : str
        Get or set the string used to replace tab characters.
    sanitize_on_paste : bool
        Enable or disable sanitizing pasted text.
    remove_empty_lines : bool
        Get or set whether to remove empty lines.
    preserve_whitespace : bool
        Get or set whether to preserve whitespace.
    """

    # INITIALIZATION
    # ///////////////////////////////////////////////////////////////

    def __init__(
        self,
        parent=None,
        tab_replacement: str = "\n",
        sanitize_on_paste: bool = True,
        remove_empty_lines: bool = True,
        preserve_whitespace: bool = False,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(parent, *args, **kwargs)

        # ////// SET WIDGET TYPE PROPERTY
        self.setProperty("type", "TabReplaceTextEdit")

        # ////// INITIALIZE PROPERTIES
        self._tab_replacement: str = tab_replacement
        self._sanitize_on_paste: bool = sanitize_on_paste
        self._remove_empty_lines: bool = remove_empty_lines
        self._preserve_whitespace: bool = preserve_whitespace

    # PROPERTIES
    # ///////////////////////////////////////////////////////////////

    @property
    def tab_replacement(self) -> str:
        """Get the string used to replace tab characters."""
        return self._tab_replacement

    @tab_replacement.setter
    def tab_replacement(self, value: str) -> None:
        """Set the string used to replace tab characters."""
        self._tab_replacement = str(value)

    @property
    def sanitize_on_paste(self) -> bool:
        """Get whether sanitizing pasted text is enabled."""
        return self._sanitize_on_paste

    @sanitize_on_paste.setter
    def sanitize_on_paste(self, value: bool) -> None:
        """Set whether sanitizing pasted text is enabled."""
        self._sanitize_on_paste = bool(value)

    @property
    def remove_empty_lines(self) -> bool:
        """Get whether empty lines are removed."""
        return self._remove_empty_lines

    @remove_empty_lines.setter
    def remove_empty_lines(self, value: bool) -> None:
        """Set whether empty lines are removed."""
        self._remove_empty_lines = bool(value)

    @property
    def preserve_whitespace(self) -> bool:
        """Get whether whitespace is preserved."""
        return self._preserve_whitespace

    @preserve_whitespace.setter
    def preserve_whitespace(self, value: bool) -> None:
        """Set whether whitespace is preserved."""
        self._preserve_whitespace = bool(value)

    # UTILITY FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def sanitize_text(self, text: str) -> str:
        """Sanitize text by replacing tabs and optionally removing empty lines."""
        # ////// REPLACE TABS
        sanitized = text.replace("\t", self._tab_replacement)

        if self._remove_empty_lines:
            # ////// SPLIT INTO LINES
            lines = sanitized.split("\n")

            # ////// FILTER EMPTY LINES
            if self._preserve_whitespace:
                # ////// KEEP LINES WITH WHITESPACE
                lines = [line for line in lines if line.strip() or line]
            else:
                # ////// REMOVE ALL EMPTY LINES BUT PRESERVE WHITESPACE
                lines = [line for line in lines if line.strip()]

            # ////// REJOIN LINES
            sanitized = "\n".join(lines)

        return sanitized

    # EVENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Overridden method from QPlainTextEdit. Modifies the behavior of the paste operation.

        Args:
            event: The event that triggers the method.
        """
        # ////// HANDLE TAB KEY
        if event.key() == Qt.Key_Tab:
            # ////// INSERT TAB REPLACEMENT
            cursor = self.textCursor()
            cursor.insertText(self._tab_replacement)
            event.accept()
            return

        # ////// HANDLE PASTE
        if self._sanitize_on_paste and event.matches(QKeySequence.StandardKey.Paste):
            # ////// GET CLIPBOARD TEXT
            clipboard = QApplication.clipboard()
            text = clipboard.text()

            # ////// SANITIZE TEXT
            text = self.sanitize_text(text)

            # ////// INSERT SANITIZED TEXT
            self.insertPlainText(text)
            event.accept()
            return

        # ////// DEFAULT BEHAVIOR
        super().keyPressEvent(event)

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refresh_style(self) -> None:
        """Refresh the widget's style (useful after dynamic stylesheet changes)."""
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
