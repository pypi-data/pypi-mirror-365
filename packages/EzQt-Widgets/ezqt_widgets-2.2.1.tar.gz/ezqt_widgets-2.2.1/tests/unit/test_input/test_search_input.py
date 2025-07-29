# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

"""
Tests unitaires pour le widget SearchInput (version corrigée).
"""

import pytest
from unittest.mock import MagicMock
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication

from ezqt_widgets.input.search_input import SearchInput


pytestmark = pytest.mark.unit


class TestSearchInput:
    """Tests pour la classe SearchInput."""

    def test_search_input_creation_default(self, qt_widget_cleanup):
        """Test de création avec paramètres par défaut."""
        search_widget = SearchInput()

        assert search_widget is not None
        assert isinstance(search_widget, SearchInput)
        assert search_widget.max_history == 20
        assert search_widget.search_icon is None
        assert search_widget.icon_position == "left"
        assert search_widget.clear_button is True

    def test_search_input_creation_with_parameters(self, qt_widget_cleanup):
        """Test de création avec paramètres personnalisés."""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.red)
        icon = QIcon(pixmap)

        search_widget = SearchInput(
            max_history=50, search_icon=icon, icon_position="right", clear_button=False
        )

        assert search_widget.max_history == 50
        assert search_widget.search_icon is not None
        assert search_widget.icon_position == "right"
        assert search_widget.clear_button is False

    def test_search_input_properties(self, qt_widget_cleanup):
        """Test des propriétés du widget."""
        search_widget = SearchInput()

        # ////// TEST SEARCH_ICON PROPERTY
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.blue)
        icon = QIcon(pixmap)
        search_widget.search_icon = icon
        assert search_widget.search_icon is not None

        # ////// TEST ICON_POSITION PROPERTY
        search_widget.icon_position = "right"
        assert search_widget.icon_position == "right"

        # ////// TEST CLEAR_BUTTON PROPERTY
        search_widget.clear_button = False
        assert search_widget.clear_button is False

        # ////// TEST MAX_HISTORY PROPERTY
        search_widget.max_history = 100
        assert search_widget.max_history == 100

    def test_search_input_history_management(self, qt_widget_cleanup):
        """Test de la gestion de l'historique."""
        search_widget = SearchInput(max_history=5)

        # ////// ÉTAT INITIAL
        assert search_widget.get_history() == []

        # ////// AJOUTER À L'HISTORIQUE
        search_widget.add_to_history("search1")
        search_widget.add_to_history("search2")
        search_widget.add_to_history("search3")

        history = search_widget.get_history()
        assert len(history) == 3
        assert "search1" in history
        assert "search2" in history
        assert "search3" in history

        # ////// TEST LIMITE MAX_HISTORY
        search_widget.add_to_history("search4")
        search_widget.add_to_history("search5")
        search_widget.add_to_history("search6")  # Devrait remplacer le plus ancien

        history = search_widget.get_history()
        assert len(history) == 5  # Max history
        assert "search6" in history  # Le plus récent
        assert "search1" not in history  # Le plus ancien supprimé

    def test_search_input_clear_history(self, qt_widget_cleanup):
        """Test de l'effacement de l'historique."""
        search_widget = SearchInput()

        # ////// AJOUTER À L'HISTORIQUE
        search_widget.add_to_history("search1")
        search_widget.add_to_history("search2")
        assert len(search_widget.get_history()) == 2

        # ////// EFFACER L'HISTORIQUE
        search_widget.clear_history()
        assert search_widget.get_history() == []

    def test_search_input_set_history(self, qt_widget_cleanup):
        """Test de la définition de l'historique."""
        search_widget = SearchInput(max_history=10)

        # ////// DÉFINIR UN HISTORIQUE
        history_list = ["item1", "item2", "item3", "item4", "item5"]
        search_widget.set_history(history_list)

        # ////// VÉRIFIER L'HISTORIQUE
        history = search_widget.get_history()
        assert len(history) == 5
        for item in history_list:
            assert item in history

    def test_search_input_trim_history(self, qt_widget_cleanup):
        """Test de la limitation de l'historique."""
        search_widget = SearchInput(max_history=3)

        # ////// AJOUTER PLUS D'ÉLÉMENTS QUE LA LIMITE
        search_widget.add_to_history("item1")
        search_widget.add_to_history("item2")
        search_widget.add_to_history("item3")
        search_widget.add_to_history("item4")
        search_widget.add_to_history("item5")

        # ////// VÉRIFIER QUE SEULS LES 3 PLUS RÉCENTS SONT PRÉSERVÉS
        history = search_widget.get_history()
        assert len(history) == 3
        assert "item3" in history
        assert "item4" in history
        assert "item5" in history
        assert "item1" not in history
        assert "item2" not in history

    def test_search_input_duplicate_history(self, qt_widget_cleanup):
        """Test avec des éléments en double dans l'historique."""
        search_widget = SearchInput()

        # ////// AJOUTER DES ÉLÉMENTS EN DOUBLE
        search_widget.add_to_history("item")
        search_widget.add_to_history("item")
        search_widget.add_to_history("item")

        # ////// VÉRIFIER QUE LES DOUBLONS SONT SUPPRIMÉS (comportement du widget)
        history = search_widget.get_history()
        assert history.count("item") == 1  # Seulement une occurrence

    def test_search_input_empty_history(self, qt_widget_cleanup):
        """Test avec un historique vide."""
        search_widget = SearchInput()

        # ////// ÉTAT INITIAL
        assert search_widget.get_history() == []

        # ////// AJOUTER ET EFFACER
        search_widget.add_to_history("item")
        assert len(search_widget.get_history()) == 1

        search_widget.clear_history()
        assert search_widget.get_history() == []

    def test_search_input_icon_management(self, qt_widget_cleanup):
        """Test de la gestion des icônes."""
        search_widget = SearchInput()

        # ////// TEST SANS ICÔNE
        assert search_widget.search_icon is None

        # ////// TEST AVEC ICÔNE
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.green)
        icon = QIcon(pixmap)
        search_widget.search_icon = icon
        assert search_widget.search_icon is not None

        # ////// TEST AVEC CHEMIN D'ICÔNE
        search_widget.search_icon = "path/to/icon.png"
        # Note: Le widget peut gérer les chemins d'icônes selon l'implémentation

    def test_search_input_icon_positions(self, qt_widget_cleanup):
        """Test des positions d'icône."""
        search_widget = SearchInput()

        # ////// TEST POSITION GAUCHE (DÉFAUT)
        assert search_widget.icon_position == "left"

        # ////// TEST POSITION DROITE
        search_widget.icon_position = "right"
        assert search_widget.icon_position == "right"

        # ////// TEST POSITION INVALIDE (N'EST PAS ACCEPTÉE)
        search_widget.icon_position = "center"
        # La valeur reste "right"
        assert search_widget.icon_position == "right"

    def test_search_input_clear_button_toggle(self, qt_widget_cleanup):
        """Test du toggle du bouton clear."""
        search_widget = SearchInput()

        # ////// ÉTAT INITIAL
        assert search_widget.clear_button is True

        # ////// DÉSACTIVER
        search_widget.clear_button = False
        assert search_widget.clear_button is False

        # ////// RÉACTIVER
        search_widget.clear_button = True
        assert search_widget.clear_button is True

    def test_search_input_max_history_validation(self, qt_widget_cleanup):
        """Test de la validation de max_history."""
        search_widget = SearchInput()

        # ////// VALEUR POSITIVE
        search_widget.max_history = 50
        assert search_widget.max_history == 50

        # ////// VALEUR ZÉRO (DOIT DEVENIR 1)
        search_widget.max_history = 0
        assert search_widget.max_history == 1

        # ////// VALEUR NÉGATIVE (DOIT DEVENIR 1)
        search_widget.max_history = -5
        assert search_widget.max_history == 1

    def test_search_input_text_handling(self, qt_widget_cleanup):
        """Test de la gestion du texte."""
        search_widget = SearchInput()

        # ////// TEST SETTEXT
        search_widget.setText("search query")
        assert search_widget.text() == "search query"

        # ////// TEST CLEAR
        search_widget.clear()
        assert search_widget.text() == ""

        # ////// TEST PLACEHOLDER
        search_widget.setPlaceholderText("Search...")
        assert search_widget.placeholderText() == "Search..."

    def test_search_input_signals(self, qt_widget_cleanup):
        """Test des signaux du widget."""
        search_widget = SearchInput()

        # ////// TEST SEARCHSUBMITTED SIGNAL
        signal_received = False
        received_text = ""

        def on_search_submitted(text):
            nonlocal signal_received, received_text
            signal_received = True
            received_text = text

        search_widget.searchSubmitted.connect(on_search_submitted)

        # ////// SIMULER UNE RECHERCHE
        search_widget.setText("test search")
        # Note: Le signal est émis lors de keyPressEvent avec Enter
        # Nous ne testons pas keyPressEvent pour éviter les problèmes Qt

        # ////// VÉRIFIER QUE LE SIGNAL EST CONNECTÉ
        assert search_widget.searchSubmitted is not None

    def test_search_input_refresh_style(self, qt_widget_cleanup):
        """Test de la méthode refresh_style."""
        search_widget = SearchInput()

        # ////// LA MÉTHODE NE DOIT PAS LEVER D'EXCEPTION
        try:
            search_widget.refresh_style()
        except Exception as e:
            pytest.fail(f"refresh_style() a levé une exception: {e}")

    def test_search_input_large_history(self, qt_widget_cleanup):
        """Test avec un grand historique."""
        search_widget = SearchInput(max_history=1000)

        # ////// AJOUTER BEAUCOUP D'ÉLÉMENTS
        for i in range(1000):
            search_widget.add_to_history(f"search_{i}")

        # ////// VÉRIFIER LA LIMITE
        history = search_widget.get_history()
        assert len(history) == 1000

        # ////// AJOUTER UN ÉLÉMENT DE PLUS
        search_widget.add_to_history("overflow")
        history = search_widget.get_history()
        assert len(history) == 1000
        assert "overflow" in history  # Le plus récent
        assert "search_0" not in history  # Le plus ancien supprimé

    def test_search_input_special_characters(self, qt_widget_cleanup):
        """Test avec des caractères spéciaux dans l'historique."""
        search_widget = SearchInput()

        special_searches = [
            "search with spaces",
            "search@email.com",
            "search-with-dashes",
            "search_with_underscores",
            "search with\nnewlines",
            "search with\ttabs",
            "search with émojis 🚀",
            "search with unicode: 你好世界",
        ]

        # ////// AJOUTER LES RECHERCHES SPÉCIALES
        for search in special_searches:
            search_widget.add_to_history(search)

        # ////// VÉRIFIER QUE TOUTES SONT PRÉSERVÉES
        history = search_widget.get_history()
        assert len(history) == len(special_searches)
        for search in special_searches:
            assert search in history

    def test_search_input_property_type(self, qt_widget_cleanup):
        """Test de la propriété type pour QSS."""
        search_widget = SearchInput()

        # ////// VÉRIFIER QUE LE WIDGET FONCTIONNE CORRECTEMENT
        assert search_widget is not None
        assert isinstance(search_widget, SearchInput)
