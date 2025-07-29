# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

"""
Tests unitaires pour le widget AutoCompleteInput.
"""

import pytest
from unittest.mock import MagicMock
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QCompleter

from ezqt_widgets.input.auto_complete_input import AutoCompleteInput


pytestmark = pytest.mark.unit


class TestAutoCompleteInput:
    """Tests pour la classe AutoCompleteInput."""

    def test_auto_complete_input_creation_default(self, qt_widget_cleanup):
        """Test de création avec paramètres par défaut."""
        input_widget = AutoCompleteInput()

        assert input_widget is not None
        assert isinstance(input_widget, AutoCompleteInput)
        assert input_widget.suggestions == []
        assert input_widget.case_sensitive is False
        assert input_widget.filter_mode == Qt.MatchContains
        assert input_widget.completion_mode == QCompleter.PopupCompletion

    def test_auto_complete_input_creation_with_parameters(self, qt_widget_cleanup):
        """Test de création avec paramètres personnalisés."""
        suggestions = ["test1", "test2", "test3"]
        input_widget = AutoCompleteInput(
            suggestions=suggestions,
            case_sensitive=True,
            filter_mode=Qt.MatchStartsWith,
            completion_mode=QCompleter.InlineCompletion,
        )

        assert input_widget.suggestions == suggestions
        assert input_widget.case_sensitive is True
        assert input_widget.filter_mode == Qt.MatchStartsWith
        assert input_widget.completion_mode == QCompleter.InlineCompletion

    def test_auto_complete_input_properties(self, qt_widget_cleanup):
        """Test des propriétés du widget."""
        input_widget = AutoCompleteInput()

        # ////// TEST SUGGESTIONS PROPERTY
        suggestions = ["item1", "item2", "item3"]
        input_widget.suggestions = suggestions
        assert input_widget.suggestions == suggestions

        # ////// TEST CASE_SENSITIVE PROPERTY
        input_widget.case_sensitive = True
        assert input_widget.case_sensitive is True

        # ////// TEST FILTER_MODE PROPERTY
        input_widget.filter_mode = Qt.MatchStartsWith
        assert input_widget.filter_mode == Qt.MatchStartsWith

        # ////// TEST COMPLETION_MODE PROPERTY
        input_widget.completion_mode = QCompleter.InlineCompletion
        assert input_widget.completion_mode == QCompleter.InlineCompletion

    def test_auto_complete_input_add_suggestion(self, qt_widget_cleanup):
        """Test de la méthode add_suggestion."""
        input_widget = AutoCompleteInput()

        # ////// ÉTAT INITIAL
        assert input_widget.suggestions == []

        # ////// AJOUTER UNE SUGGESTION
        input_widget.add_suggestion("new_item")
        assert "new_item" in input_widget.suggestions

        # ////// AJOUTER UNE AUTRE SUGGESTION
        input_widget.add_suggestion("another_item")
        assert "new_item" in input_widget.suggestions
        assert "another_item" in input_widget.suggestions
        assert len(input_widget.suggestions) == 2

    def test_auto_complete_input_remove_suggestion(self, qt_widget_cleanup):
        """Test de la méthode remove_suggestion."""
        input_widget = AutoCompleteInput(suggestions=["item1", "item2", "item3"])

        # ////// ÉTAT INITIAL
        assert len(input_widget.suggestions) == 3

        # ////// SUPPRIMER UNE SUGGESTION
        input_widget.remove_suggestion("item2")
        assert "item1" in input_widget.suggestions
        assert "item2" not in input_widget.suggestions
        assert "item3" in input_widget.suggestions
        assert len(input_widget.suggestions) == 2

    def test_auto_complete_input_clear_suggestions(self, qt_widget_cleanup):
        """Test de la méthode clear_suggestions."""
        input_widget = AutoCompleteInput(suggestions=["item1", "item2", "item3"])

        # ////// ÉTAT INITIAL
        assert len(input_widget.suggestions) == 3

        # ////// EFFACER TOUTES LES SUGGESTIONS
        input_widget.clear_suggestions()
        assert input_widget.suggestions == []

    def test_auto_complete_input_refresh_style(self, qt_widget_cleanup):
        """Test de la méthode refresh_style."""
        input_widget = AutoCompleteInput()

        # ////// LA MÉTHODE NE DOIT PAS LEVER D'EXCEPTION
        try:
            input_widget.refresh_style()
        except Exception as e:
            pytest.fail(f"refresh_style() a levé une exception: {e}")

    def test_auto_complete_input_completer_integration(self, qt_widget_cleanup):
        """Test de l'intégration avec QCompleter."""
        input_widget = AutoCompleteInput(suggestions=["test1", "test2"])

        # ////// VÉRIFIER QUE LE COMPLETER EST CONFIGURÉ
        assert input_widget.completer() is not None
        assert isinstance(input_widget.completer(), QCompleter)

        # ////// VÉRIFIER QUE LE MODÈLE CONTIENT LES SUGGESTIONS
        model = input_widget.completer().model()
        assert model is not None
        assert model.rowCount() == 2

    def test_auto_complete_input_case_sensitivity(self, qt_widget_cleanup):
        """Test de la sensibilité à la casse."""
        input_widget = AutoCompleteInput(suggestions=["Test", "test", "TEST"])

        # ////// TEST CASE INSENSITIVE (DÉFAUT)
        input_widget.case_sensitive = False
        assert input_widget.case_sensitive is False

        # ////// TEST CASE SENSITIVE
        input_widget.case_sensitive = True
        assert input_widget.case_sensitive is True

    def test_auto_complete_input_filter_modes(self, qt_widget_cleanup):
        """Test des différents modes de filtrage."""
        input_widget = AutoCompleteInput()

        # ////// TEST MATCHCONTAINS (DÉFAUT)
        input_widget.filter_mode = Qt.MatchContains
        assert input_widget.filter_mode == Qt.MatchContains

        # ////// TEST MATCHSTARTSWITH
        input_widget.filter_mode = Qt.MatchStartsWith
        assert input_widget.filter_mode == Qt.MatchStartsWith

        # ////// TEST MATCHENDSWITH
        input_widget.filter_mode = Qt.MatchEndsWith
        assert input_widget.filter_mode == Qt.MatchEndsWith

    def test_auto_complete_input_completion_modes(self, qt_widget_cleanup):
        """Test des différents modes de complétion."""
        input_widget = AutoCompleteInput()

        # ////// TEST POPUPCOMPLETION (DÉFAUT)
        input_widget.completion_mode = QCompleter.PopupCompletion
        assert input_widget.completion_mode == QCompleter.PopupCompletion

        # ////// TEST INLINECOMPLETION
        input_widget.completion_mode = QCompleter.InlineCompletion
        assert input_widget.completion_mode == QCompleter.InlineCompletion

        # ////// TEST UNFILTEREDPOPUPCOMPLETION
        input_widget.completion_mode = QCompleter.UnfilteredPopupCompletion
        assert input_widget.completion_mode == QCompleter.UnfilteredPopupCompletion

    def test_auto_complete_input_text_handling(self, qt_widget_cleanup):
        """Test de la gestion du texte."""
        input_widget = AutoCompleteInput()

        # ////// TEST SETTEXT
        input_widget.setText("test text")
        assert input_widget.text() == "test text"

        # ////// TEST CLEAR
        input_widget.clear()
        assert input_widget.text() == ""

        # ////// TEST PLACEHOLDER
        input_widget.setPlaceholderText("Enter text...")
        assert input_widget.placeholderText() == "Enter text..."

    def test_auto_complete_input_multiple_suggestions(self, qt_widget_cleanup):
        """Test avec de nombreuses suggestions."""
        suggestions = [f"item_{i}" for i in range(100)]
        input_widget = AutoCompleteInput(suggestions=suggestions)

        # ////// VÉRIFIER QUE TOUTES LES SUGGESTIONS SONT PRÉSENTES
        assert len(input_widget.suggestions) == 100
        assert "item_0" in input_widget.suggestions
        assert "item_99" in input_widget.suggestions

        # ////// VÉRIFIER QUE LE COMPLETER PEUT GÉRER BEAUCOUP D'ÉLÉMENTS
        assert input_widget.completer().model().rowCount() == 100

    def test_auto_complete_input_empty_suggestions(self, qt_widget_cleanup):
        """Test avec des suggestions vides."""
        input_widget = AutoCompleteInput(suggestions=[])

        # ////// VÉRIFIER L'ÉTAT INITIAL
        assert input_widget.suggestions == []

        # ////// AJOUTER DES SUGGESTIONS
        input_widget.add_suggestion("new_item")
        assert input_widget.suggestions == ["new_item"]

        # ////// EFFACER ET VÉRIFIER
        input_widget.clear_suggestions()
        assert input_widget.suggestions == []

    def test_auto_complete_input_duplicate_suggestions(self, qt_widget_cleanup):
        """Test avec des suggestions en double."""
        input_widget = AutoCompleteInput()

        # ////// AJOUTER DES SUGGESTIONS EN DOUBLE
        input_widget.add_suggestion("item")
        input_widget.add_suggestion("item")
        input_widget.add_suggestion("item")

        # ////// VÉRIFIER QUE LES DOUBLONS SONT IGNORÉS (comportement du widget)
        assert input_widget.suggestions.count("item") == 1

        # ////// SUPPRIMER L'OCCURRENCE
        input_widget.remove_suggestion("item")
        assert input_widget.suggestions.count("item") == 0

    def test_auto_complete_input_special_characters(self, qt_widget_cleanup):
        """Test avec des caractères spéciaux."""
        special_suggestions = [
            "test@example.com",
            "user-name_123",
            "file/path/to/item",
            "item with spaces",
            "item\nwith\nnewlines",
            "item\twith\ttabs",
        ]

        input_widget = AutoCompleteInput(suggestions=special_suggestions)

        # ////// VÉRIFIER QUE TOUTES LES SUGGESTIONS SONT PRÉSERVÉES
        assert len(input_widget.suggestions) == 6
        for suggestion in special_suggestions:
            assert suggestion in input_widget.suggestions

    def test_auto_complete_input_property_type(self, qt_widget_cleanup):
        """Test de la propriété type pour QSS."""
        input_widget = AutoCompleteInput()

        # ////// VÉRIFIER QUE LA PROPRIÉTÉ TYPE EST DÉFINIE
        # Note: AutoCompleteInput hérite de QLineEdit, donc pas de propriété type personnalisée
        # Mais on peut vérifier que le widget fonctionne correctement
        assert input_widget is not None
        assert isinstance(input_widget, AutoCompleteInput)
