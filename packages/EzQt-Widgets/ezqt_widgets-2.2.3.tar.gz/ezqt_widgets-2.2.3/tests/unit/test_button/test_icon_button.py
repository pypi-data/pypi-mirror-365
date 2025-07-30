# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

"""
Tests unitaires pour le widget IconButton.
"""

import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication

from ezqt_widgets.button.icon_button import (
    IconButton,
    colorize_pixmap,
    load_icon_from_source,
)


pytestmark = pytest.mark.unit


class TestColorizePixmap:
    """Tests pour la fonction colorize_pixmap."""

    def test_colorize_pixmap_basic(self, qt_widget_cleanup):
        """Test de base pour colorize_pixmap."""
        # ////// CRÉER UN PIXMAP DE TEST
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.white)

        # ////// TESTER LA COLORISATION
        result = colorize_pixmap(pixmap, "#FF0000", 0.8)

        # ////// VÉRIFICATIONS
        assert result is not None
        assert result.size() == pixmap.size()
        assert result.width() == 16
        assert result.height() == 16

    def test_colorize_pixmap_transparent(self, qt_widget_cleanup):
        """Test avec opacité transparente."""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.white)

        result = colorize_pixmap(pixmap, "#00FF00", 0.0)

        assert result is not None
        assert result.size() == pixmap.size()


class TestLoadIconFromSource:
    """Tests pour la fonction load_icon_from_source."""

    def test_load_icon_from_none(self, qt_widget_cleanup):
        """Test avec source None."""
        result = load_icon_from_source(None)
        assert result is None

    def test_load_icon_from_qicon(self, qt_widget_cleanup):
        """Test avec QIcon existant."""
        # ////// CRÉER UN QICON DE TEST
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.red)
        icon = QIcon(pixmap)

        result = load_icon_from_source(icon)

        assert result is not None
        assert isinstance(result, QIcon)

    def test_load_icon_from_file_path(self, mock_icon_path):
        """Test avec chemin de fichier."""
        result = load_icon_from_source(mock_icon_path)

        assert result is not None
        assert isinstance(result, QIcon)

    def test_load_icon_from_svg_path(self, mock_svg_path):
        """Test avec fichier SVG."""
        result = load_icon_from_source(mock_svg_path)

        assert result is not None
        assert isinstance(result, QIcon)

    @patch("requests.get")
    def test_load_icon_from_url(self, mock_get, qt_widget_cleanup):
        """Test avec URL."""
        # ////// MOCKER LA RÉPONSE HTTP
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.headers = {"Content-Type": "image/png"}

        # ////// CRÉER UN PNG VALIDE EN UTILISANT QPIXMAP
        from PySide6.QtGui import QPixmap, QPainter, QColor

        # Créer un pixmap 16x16 rouge
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(255, 0, 0))  # Rouge

        # Convertir en PNG bytes
        from PySide6.QtCore import QBuffer, QIODevice

        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        pixmap.save(buffer, "PNG")
        png_content = buffer.data()
        buffer.close()

        mock_response.content = png_content
        mock_get.return_value = mock_response

        result = load_icon_from_source("https://example.com/icon.png")

        assert result is not None
        assert isinstance(result, QIcon)
        mock_get.assert_called_once_with("https://example.com/icon.png", timeout=5)

    @patch("requests.get")
    def test_load_icon_from_invalid_url(self, mock_get):
        """Test avec URL invalide."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("Network error")
        mock_get.return_value = mock_response

        result = load_icon_from_source("https://invalid-url.com/icon.png")

        assert result is None


class TestIconButton:
    """Tests pour la classe IconButton."""

    def test_icon_button_creation_default(self, qt_widget_cleanup):
        """Test de création avec paramètres par défaut."""
        button = IconButton()

        assert button is not None
        assert isinstance(button, IconButton)
        assert button.text == ""
        assert button.icon_size == QSize(20, 20)
        assert button.text_visible is True
        assert button.spacing == 10

    def test_icon_button_creation_with_parameters(
        self, qt_widget_cleanup, mock_icon_path
    ):
        """Test de création avec paramètres personnalisés."""
        icon = QIcon(mock_icon_path)
        button = IconButton(
            icon=icon,
            text="Test Button",
            icon_size=QSize(32, 32),
            text_visible=False,
            spacing=15,
        )

        assert button.icon is not None
        assert button.text == "Test Button"
        assert button.icon_size == QSize(32, 32)
        assert button.text_visible is False
        assert button.spacing == 15

    def test_icon_button_properties(self, qt_widget_cleanup):
        """Test des propriétés du bouton."""
        button = IconButton()

        # ////// TEST ICON PROPERTY
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.blue)
        icon = QIcon(pixmap)

        button.icon = icon
        assert button.icon is not None

        # ////// TEST TEXT PROPERTY
        button.text = "New Text"
        assert button.text == "New Text"

        # ////// TEST ICON_SIZE PROPERTY
        button.icon_size = QSize(24, 24)
        assert button.icon_size == QSize(24, 24)

        # ////// TEST TEXT_VISIBLE PROPERTY
        button.text_visible = False
        assert button.text_visible is False

        # ////// TEST SPACING PROPERTY
        button.spacing = 20
        assert button.spacing == 20

    def test_icon_button_signals(self, qt_widget_cleanup):
        """Test des signaux du bouton."""
        button = IconButton()

        # ////// TEST ICONCHANGED SIGNAL
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.green)
        icon = QIcon(pixmap)

        signal_received = False

        def on_icon_changed(new_icon):
            nonlocal signal_received
            signal_received = True
            assert new_icon is not None

        button.iconChanged.connect(on_icon_changed)
        button.icon = icon

        # ////// VÉRIFIER QUE LE SIGNAL A ÉTÉ ÉMIS
        assert signal_received

        # ////// TEST TEXTCHANGED SIGNAL
        text_signal_received = False

        def on_text_changed(new_text):
            nonlocal text_signal_received
            text_signal_received = True
            assert new_text == "Signal Test"

        button.textChanged.connect(on_text_changed)
        button.text = "Signal Test"

        # ////// VÉRIFIER QUE LE SIGNAL A ÉTÉ ÉMIS
        assert text_signal_received

    def test_icon_button_methods(self, qt_widget_cleanup):
        """Test des méthodes du bouton."""
        button = IconButton(text="Test", icon=QIcon())

        # ////// TEST CLEAR_ICON
        button.clear_icon()
        assert button.icon is None

        # ////// TEST CLEAR_TEXT
        button.clear_text()
        assert button.text == ""

        # ////// TEST TOGGLE_TEXT_VISIBILITY
        initial_visibility = button.text_visible
        button.toggle_text_visibility()
        assert button.text_visible != initial_visibility

        button.toggle_text_visibility()
        assert button.text_visible == initial_visibility

    def test_icon_button_size_hints(self, qt_widget_cleanup):
        """Test des méthodes de taille."""
        button = IconButton(text="Test Button", icon=QIcon())

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

    def test_icon_button_set_icon_color(self, qt_widget_cleanup):
        """Test de la méthode set_icon_color."""
        # ////// CRÉER UN BOUTON AVEC ICÔNE
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.white)
        icon = QIcon(pixmap)
        button = IconButton(icon=icon)

        # ////// TESTER LA COLORISATION
        button.set_icon_color("#FF0000", 0.7)

        # ////// VÉRIFIER QUE L'ICÔNE A ÉTÉ MODIFIÉE
        assert button.icon is not None

    def test_icon_button_refresh_style(self, qt_widget_cleanup):
        """Test de la méthode refresh_style."""
        button = IconButton()

        # ////// LA MÉTHODE NE DOIT PAS LEVER D'EXCEPTION
        try:
            button.refresh_style()
        except Exception as e:
            pytest.fail(f"refresh_style() a levé une exception: {e}")

    def test_icon_button_minimum_dimensions(self, qt_widget_cleanup):
        """Test des dimensions minimales."""
        button = IconButton(min_width=100, min_height=50)

        assert button.min_width == 100
        assert button.min_height == 50

        # ////// MODIFIER LES DIMENSIONS
        button.min_width = 150
        button.min_height = 75

        assert button.min_width == 150
        assert button.min_height == 75

        # ////// TESTER AVEC NONE
        button.min_width = None
        button.min_height = None

        assert button.min_width is None
        assert button.min_height is None
