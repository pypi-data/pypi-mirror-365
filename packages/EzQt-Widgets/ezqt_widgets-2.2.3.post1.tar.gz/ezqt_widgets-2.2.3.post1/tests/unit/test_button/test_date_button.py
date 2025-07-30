# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

"""
Tests unitaires pour le widget DateButton.
"""

import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtCore import QSize, Qt, QDate
from PySide6.QtGui import QIcon, QPixmap, QMouseEvent
from PySide6.QtWidgets import QApplication

from ezqt_widgets.button.date_button import (
    DateButton,
    DatePickerDialog,
    format_date,
    parse_date,
    get_calendar_icon,
)


pytestmark = pytest.mark.unit


class TestUtilityFunctions:
    """Tests pour les fonctions utilitaires."""

    def test_format_date_valid(self, qt_widget_cleanup):
        """Test de format_date avec une date valide."""
        date = QDate(2024, 1, 15)
        result = format_date(date, "dd/MM/yyyy")
        assert result == "15/01/2024"

    def test_format_date_invalid(self, qt_widget_cleanup):
        """Test de format_date avec une date invalide."""
        date = QDate()
        result = format_date(date, "dd/MM/yyyy")
        assert result == ""

    def test_format_date_custom_format(self, qt_widget_cleanup):
        """Test de format_date avec un format personnalisé."""
        date = QDate(2024, 1, 15)
        result = format_date(date, "yyyy-MM-dd")
        assert result == "2024-01-15"

    def test_parse_date_valid(self, qt_widget_cleanup):
        """Test de parse_date avec une chaîne valide."""
        result = parse_date("15/01/2024", "dd/MM/yyyy")
        assert result.isValid()
        assert result.year() == 2024
        assert result.month() == 1
        assert result.day() == 15

    def test_parse_date_invalid(self, qt_widget_cleanup):
        """Test de parse_date avec une chaîne invalide."""
        result = parse_date("invalid", "dd/MM/yyyy")
        assert not result.isValid()

    def test_get_calendar_icon(self, qt_widget_cleanup):
        """Test de get_calendar_icon."""
        icon = get_calendar_icon()
        assert icon is not None
        assert isinstance(icon, QIcon)
        assert not icon.isNull()


class TestDatePickerDialog:
    """Tests pour la classe DatePickerDialog."""

    def test_date_picker_dialog_creation(self, qt_widget_cleanup):
        """Test de création du dialogue."""
        dialog = DatePickerDialog()
        assert dialog is not None
        assert isinstance(dialog, DatePickerDialog)

    def test_date_picker_dialog_with_date(self, qt_widget_cleanup):
        """Test de création avec une date."""
        date = QDate(2024, 1, 15)
        dialog = DatePickerDialog(current_date=date)
        assert dialog.selected_date() == date

    def test_date_picker_dialog_selected_date(self, qt_widget_cleanup):
        """Test de la propriété selected_date."""
        dialog = DatePickerDialog()
        assert dialog.selected_date() is None


class TestDateButton:
    """Tests pour la classe DateButton."""

    def test_date_button_creation_default(self, qt_widget_cleanup):
        """Test de création avec paramètres par défaut."""
        button = DateButton()

        assert button is not None
        assert isinstance(button, DateButton)
        assert button.date_format == "dd/MM/yyyy"
        assert button.placeholder == "Sélectionner une date"
        assert button.show_calendar_icon is True
        assert button.icon_size == QSize(16, 16)

    def test_date_button_creation_with_parameters(self, qt_widget_cleanup):
        """Test de création avec paramètres personnalisés."""
        date = QDate(2024, 1, 15)
        button = DateButton(
            date=date,
            date_format="yyyy-MM-dd",
            placeholder="Choisir date",
            show_calendar_icon=False,
            icon_size=QSize(24, 24),
        )

        assert button.date == date
        assert button.date_format == "yyyy-MM-dd"
        assert button.placeholder == "Choisir date"
        assert button.show_calendar_icon is False
        assert button.icon_size == QSize(24, 24)

    def test_date_button_creation_with_string_date(self, qt_widget_cleanup):
        """Test de création avec une date en chaîne."""
        button = DateButton(date="15/01/2024")

        assert button.date.isValid()
        assert button.date.year() == 2024
        assert button.date.month() == 1
        assert button.date.day() == 15

    def test_date_button_properties(self, qt_widget_cleanup):
        """Test des propriétés du bouton."""
        button = DateButton()

        # ////// TEST DATE PROPERTY
        date = QDate(2024, 1, 15)
        button.date = date
        assert button.date == date

        # ////// TEST DATE_STRING PROPERTY
        button.date_string = "20/02/2024"
        assert button.date.year() == 2024
        assert button.date.month() == 2
        assert button.date.day() == 20

        # ////// TEST DATE_FORMAT PROPERTY
        button.date_format = "yyyy-MM-dd"
        assert button.date_format == "yyyy-MM-dd"

        # ////// TEST PLACEHOLDER PROPERTY
        button.placeholder = "Nouveau placeholder"
        assert button.placeholder == "Nouveau placeholder"

        # ////// TEST SHOW_CALENDAR_ICON PROPERTY
        button.show_calendar_icon = False
        assert button.show_calendar_icon is False

        # ////// TEST ICON_SIZE PROPERTY
        button.icon_size = QSize(32, 32)
        assert button.icon_size == QSize(32, 32)

    def test_date_button_signals(self, qt_widget_cleanup):
        """Test des signaux du bouton."""
        button = DateButton()

        # ////// TEST DATECHANGED SIGNAL
        date = QDate(2024, 1, 15)

        signal_received = False

        def on_date_changed(new_date):
            nonlocal signal_received
            signal_received = True
            assert new_date == date

        button.dateChanged.connect(on_date_changed)
        button.date = date

        # ////// VÉRIFIER QUE LE SIGNAL A ÉTÉ ÉMIS
        assert signal_received

    def test_date_button_methods(self, qt_widget_cleanup):
        """Test des méthodes du bouton."""
        button = DateButton()

        # ////// TEST CLEAR_DATE
        button.date = QDate(2024, 1, 15)
        button.clear_date()
        assert not button.date.isValid()

        # ////// TEST SET_TODAY
        button.set_today()
        assert button.date.isValid()
        assert button.date == QDate.currentDate()

    @patch("ezqt_widgets.button.date_button.DatePickerDialog")
    def test_date_button_open_calendar(self, mock_dialog_class, qt_widget_cleanup):
        """Test de la méthode open_calendar."""
        button = DateButton()

        # ////// MOCKER LE DIALOGUE
        mock_dialog = MagicMock()
        mock_dialog.selected_date.return_value = QDate(2024, 1, 15)
        mock_dialog_class.return_value = mock_dialog

        # ////// TESTER L'OUVERTURE DU CALENDRIER
        button.open_calendar()

        # ////// VÉRIFIER QUE LE DIALOGUE A ÉTÉ CRÉÉ ET EXÉCUTÉ
        mock_dialog_class.assert_called_once()
        mock_dialog.exec.assert_called_once()

    def test_date_button_size_hints(self, qt_widget_cleanup):
        """Test des méthodes de taille."""
        button = DateButton(text="Test Button")

        # ////// TEST SIZEHINT
        size_hint = button.sizeHint()
        assert size_hint is not None
        assert isinstance(size_hint, QSize)
        assert size_hint.width() > 0
        assert size_hint.height() > 0

        # ////// TEST MINIMUMSIZEHINT
        min_size_hint = button.minimumSizeHint()
        assert min_size_hint is not None
        assert isinstance(min_size_hint, QSize)
        assert min_size_hint.width() > 0
        assert min_size_hint.height() > 0

    def test_date_button_refresh_style(self, qt_widget_cleanup):
        """Test de la méthode refresh_style."""
        button = DateButton()

        # ////// LA MÉTHODE NE DOIT PAS LEVER D'EXCEPTION
        try:
            button.refresh_style()
        except Exception as e:
            pytest.fail(f"refresh_style() a levé une exception: {e}")

    def test_date_button_minimum_dimensions(self, qt_widget_cleanup):
        """Test des dimensions minimales."""
        button = DateButton(min_width=150, min_height=50)

        assert button.min_width == 150
        assert button.min_height == 50

        # ////// MODIFIER LES DIMENSIONS
        button.min_width = 200
        button.min_height = 75

        assert button.min_width == 200
        assert button.min_height == 75

        # ////// TESTER AVEC NONE
        button.min_width = None
        button.min_height = None

        assert button.min_width is None
        assert button.min_height is None

    def test_date_button_mouse_press_event(self, qt_widget_cleanup):
        """Test de l'événement mousePressEvent."""
        button = DateButton()

        # ////// CRÉER UN VRAI ÉVÉNEMENT MOUSE QT
        from PySide6.QtCore import QPoint
        from PySide6.QtGui import QMouseEvent

        # Créer un vrai événement mouse press
        event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            QPoint(10, 10),
            QPoint(10, 10),
            Qt.LeftButton,
            Qt.LeftButton,
            Qt.NoModifier,
        )

        # ////// TESTER QUE L'ÉVÉNEMENT NE LÈVE PAS D'EXCEPTION
        try:
            button.mousePressEvent(event)
        except Exception as e:
            pytest.fail(f"mousePressEvent() a levé une exception: {e}")

    def test_date_button_display_with_date(self, qt_widget_cleanup):
        """Test de l'affichage avec une date."""
        date = QDate(2024, 1, 15)
        button = DateButton(date=date)

        # ////// VÉRIFIER QUE LA DATE EST AFFICHÉE
        assert button.date_string == "15/01/2024"

    def test_date_button_display_without_date(self, qt_widget_cleanup):
        """Test de l'affichage sans date."""
        button = DateButton()

        # ////// VÉRIFIER QUE LE WIDGET AFFICHE UNE DATE
        # Note: DateButton initialise avec la date actuelle par défaut
        assert button.date_string != ""
        assert button.date.isValid()

        # ////// EFFACER LA DATE
        button.clear_date()

        # ////// VÉRIFIER QUE LA DATE EST EFFACÉE
        # Note: clear_date() définit une QDate invalide, donc date_string retourne ""
        assert button.date_string == ""
        assert not button.date.isValid()

        # ////// VÉRIFIER QUE LE LABEL AFFICHE LE PLACEHOLDER
        # Le label interne devrait afficher le placeholder
        assert button.date_label.text() == button.placeholder

    def test_date_button_custom_format(self, qt_widget_cleanup):
        """Test avec un format personnalisé."""
        date = QDate(2024, 1, 15)
        button = DateButton(date=date, date_format="yyyy-MM-dd")

        # ////// VÉRIFIER QUE LE FORMAT EST APPLIQUÉ
        assert button.date_string == "2024-01-15"
