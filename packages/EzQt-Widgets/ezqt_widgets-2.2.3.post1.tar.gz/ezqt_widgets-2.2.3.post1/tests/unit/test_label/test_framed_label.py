# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

"""
Tests unitaires pour le widget FramedLabel.
"""

import pytest
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication

from ezqt_widgets.label.framed_label import FramedLabel


pytestmark = pytest.mark.unit


class TestFramedLabel:
    """Tests pour la classe FramedLabel."""

    def test_framed_label_creation_default(self, qt_widget_cleanup):
        """Test de création avec paramètres par défaut."""
        label = FramedLabel()

        assert label is not None
        assert isinstance(label, FramedLabel)
        assert label.text == ""
        assert label.alignment == Qt.AlignmentFlag.AlignCenter
        assert label.min_width is None
        assert label.min_height is None

    def test_framed_label_creation_with_parameters(self, qt_widget_cleanup):
        """Test de création avec paramètres personnalisés."""
        label = FramedLabel(
            text="Test Label",
            alignment=Qt.AlignmentFlag.AlignLeft,
            style_sheet="background-color: red;",
            min_width=200,
            min_height=50,
        )

        assert label.text == "Test Label"
        assert label.alignment == Qt.AlignmentFlag.AlignLeft
        assert label.min_width == 200
        assert label.min_height == 50

    def test_framed_label_properties(self, qt_widget_cleanup):
        """Test des propriétés du label."""
        label = FramedLabel()

        # ////// TEST TEXT PROPERTY
        label.text = "New Text"
        assert label.text == "New Text"

        # ////// TEST ALIGNMENT PROPERTY
        label.alignment = Qt.AlignmentFlag.AlignRight
        assert label.alignment == Qt.AlignmentFlag.AlignRight

        # ////// TEST MIN_WIDTH PROPERTY
        label.min_width = 150
        assert label.min_width == 150

        # ////// TEST MIN_HEIGHT PROPERTY
        label.min_height = 40
        assert label.min_height == 40

        # ////// TESTER AVEC NONE
        label.min_width = None
        label.min_height = None
        assert label.min_width is None
        assert label.min_height is None

    def test_framed_label_signals(self, qt_widget_cleanup):
        """Test des signaux du label."""
        label = FramedLabel()

        # ////// TEST TEXTCHANGED SIGNAL
        signal_received = False
        received_text = ""

        def on_text_changed(text):
            nonlocal signal_received, received_text
            signal_received = True
            received_text = text

        label.textChanged.connect(on_text_changed)

        # ////// CHANGER LE TEXTE
        label.text = "Signal Test"

        # ////// VÉRIFIER QUE LE SIGNAL A ÉTÉ ÉMIS
        assert signal_received
        assert received_text == "Signal Test"

    def test_framed_label_size_hints(self, qt_widget_cleanup):
        """Test des méthodes de taille."""
        label = FramedLabel(text="Test Label")

        # ////// TEST MINIMUMSIZEHINT
        min_size_hint = label.minimumSizeHint()
        assert min_size_hint is not None
        assert isinstance(min_size_hint, QSize)
        assert min_size_hint.width() > 0
        assert min_size_hint.height() > 0

    def test_framed_label_refresh_style(self, qt_widget_cleanup):
        """Test de la méthode refresh_style."""
        label = FramedLabel()

        # ////// LA MÉTHODE NE DOIT PAS LEVER D'EXCEPTION
        try:
            label.refresh_style()
        except Exception as e:
            pytest.fail(f"refresh_style() a levé une exception: {e}")

    def test_framed_label_alignment_options(self, qt_widget_cleanup):
        """Test des différentes options d'alignement."""
        # ////// TEST ALIGNMENT LEFT
        label_left = FramedLabel(alignment=Qt.AlignmentFlag.AlignLeft)
        assert label_left.alignment == Qt.AlignmentFlag.AlignLeft

        # ////// TEST ALIGNMENT CENTER
        label_center = FramedLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        assert label_center.alignment == Qt.AlignmentFlag.AlignCenter

        # ////// TEST ALIGNMENT RIGHT
        label_right = FramedLabel(alignment=Qt.AlignmentFlag.AlignRight)
        assert label_right.alignment == Qt.AlignmentFlag.AlignRight

        # ////// TEST ALIGNMENT TOP
        label_top = FramedLabel(alignment=Qt.AlignmentFlag.AlignTop)
        assert label_top.alignment == Qt.AlignmentFlag.AlignTop

        # ////// TEST ALIGNMENT BOTTOM
        label_bottom = FramedLabel(alignment=Qt.AlignmentFlag.AlignBottom)
        assert label_bottom.alignment == Qt.AlignmentFlag.AlignBottom

    def test_framed_label_text_changes(self, qt_widget_cleanup):
        """Test des changements de texte."""
        label = FramedLabel()

        # ////// TEXTE VIDE
        label.text = ""
        assert label.text == ""

        # ////// TEXTE AVEC ESPACES
        label.text = "   Text with spaces   "
        assert label.text == "   Text with spaces   "

        # ////// TEXTE LONG
        long_text = "This is a very long text that should be handled properly by the FramedLabel widget"
        label.text = long_text
        assert label.text == long_text

        # ////// TEXTE AVEC CARACTÈRES SPÉCIAUX
        special_text = "Text with special chars: éàùç€£¥"
        label.text = special_text
        assert label.text == special_text

    def test_framed_label_style_sheet(self, qt_widget_cleanup):
        """Test de l'application de stylesheet."""
        # ////// CRÉER UN LABEL AVEC STYLESHEET
        style_sheet = "background-color: #FF0000; color: white; border: 2px solid blue;"
        label = FramedLabel(style_sheet=style_sheet)

        # ////// VÉRIFIER QUE LE STYLESHEET EST APPLIQUÉ
        # Note: On ne peut pas facilement tester le rendu visuel dans les tests unitaires
        # mais on peut vérifier que le widget est créé sans erreur
        assert label is not None
        assert isinstance(label, FramedLabel)

    def test_framed_label_dimensions(self, qt_widget_cleanup):
        """Test des dimensions minimales."""
        label = FramedLabel(min_width=100, min_height=30)

        # ////// VÉRIFIER LES DIMENSIONS INITIALES
        assert label.min_width == 100
        assert label.min_height == 30

        # ////// MODIFIER LES DIMENSIONS
        label.min_width = 200
        label.min_height = 50
        assert label.min_width == 200
        assert label.min_height == 50

        # ////// TESTER AVEC DES VALEURS NÉGATIVES
        label.min_width = -10
        label.min_height = -5
        assert label.min_width == -10
        assert label.min_height == -5

    def test_framed_label_property_type(self, qt_widget_cleanup):
        """Test de la propriété type pour QSS."""
        label = FramedLabel()

        # ////// VÉRIFIER QUE LA PROPRIÉTÉ TYPE EST DÉFINIE
        assert label.property("type") == "FramedLabel"

    def test_framed_label_multiple_instances(self, qt_widget_cleanup):
        """Test de plusieurs instances."""
        # ////// CRÉER PLUSIEURS INSTANCES
        label1 = FramedLabel(text="Label 1")
        label2 = FramedLabel(text="Label 2")
        label3 = FramedLabel(text="Label 3")

        # ////// VÉRIFIER QUE CHAQUE INSTANCE EST INDÉPENDANTE
        assert label1.text == "Label 1"
        assert label2.text == "Label 2"
        assert label3.text == "Label 3"

        # ////// MODIFIER UNE INSTANCE
        label1.text = "Modified Label 1"
        assert label1.text == "Modified Label 1"
        assert label2.text == "Label 2"  # Non affecté
        assert label3.text == "Label 3"  # Non affecté

    def test_framed_label_empty_constructor(self, qt_widget_cleanup):
        """Test du constructeur sans paramètres."""
        label = FramedLabel()

        # ////// VÉRIFIER LES VALEURS PAR DÉFAUT
        assert label.text == ""
        assert label.alignment == Qt.AlignmentFlag.AlignCenter
        assert label.min_width is None
        assert label.min_height is None

    def test_framed_label_text_property_changes(self, qt_widget_cleanup):
        """Test des changements de la propriété text."""
        label = FramedLabel()

        # ////// CHANGER LE TEXTE PLUSIEURS FOIS
        label.text = "First text"
        assert label.text == "First text"

        label.text = "Second text"
        assert label.text == "Second text"

        label.text = "Third text"
        assert label.text == "Third text"

        # ////// REVENIR À UN TEXTE VIDE
        label.text = ""
        assert label.text == ""
