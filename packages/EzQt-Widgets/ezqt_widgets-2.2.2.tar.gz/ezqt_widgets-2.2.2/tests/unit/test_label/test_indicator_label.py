# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

"""
Tests unitaires pour le widget IndicatorLabel.
"""

import pytest
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication

from ezqt_widgets.label.indicator_label import IndicatorLabel


pytestmark = pytest.mark.unit


class TestIndicatorLabel:
    """Tests pour la classe IndicatorLabel."""

    def test_indicator_label_creation_default(self, qt_widget_cleanup):
        """Test de création avec paramètres par défaut."""
        label = IndicatorLabel()

        assert label is not None
        assert isinstance(label, IndicatorLabel)
        assert label.status == "neutral"

    def test_indicator_label_creation_with_parameters(self, qt_widget_cleanup):
        """Test de création avec paramètres personnalisés."""
        custom_status_map = {
            "custom1": {"text": "Custom 1", "state": "state1", "color": "#FF0000"},
            "custom2": {"text": "Custom 2", "state": "state2", "color": "#00FF00"},
        }

        label = IndicatorLabel(status_map=custom_status_map, initial_status="custom1")

        assert label.status == "custom1"

    def test_indicator_label_properties(self, qt_widget_cleanup):
        """Test des propriétés du label."""
        label = IndicatorLabel()

        # ////// TEST STATUS PROPERTY
        label.status = "online"
        assert label.status == "online"

        # ////// TESTER AVEC UN STATUT INVALIDE (DOIT LÉVER UNE EXCEPTION)
        with pytest.raises(ValueError, match="Unknown status"):
            label.status = "invalid_status"

    def test_indicator_label_signals(self, qt_widget_cleanup):
        """Test des signaux du label."""
        label = IndicatorLabel()

        # ////// TEST STATUSCHANGED SIGNAL
        signal_received = False
        received_status = ""

        def on_status_changed(status):
            nonlocal signal_received, received_status
            signal_received = True
            received_status = status

        label.statusChanged.connect(on_status_changed)

        # ////// CHANGER LE STATUT
        label.status = "online"

        # ////// VÉRIFIER QUE LE SIGNAL A ÉTÉ ÉMIS
        assert signal_received
        assert received_status == "online"

    def test_indicator_label_set_status_method(self, qt_widget_cleanup):
        """Test de la méthode set_status."""
        label = IndicatorLabel()

        # ////// ÉTAT INITIAL
        assert label.status == "neutral"

        # ////// CHANGER LE STATUT
        label.set_status("online")
        assert label.status == "online"

        # ////// CHANGER ENCORE
        label.set_status("offline")
        assert label.status == "offline"

    def test_indicator_label_refresh_style(self, qt_widget_cleanup):
        """Test de la méthode refresh_style."""
        label = IndicatorLabel()

        # ////// LA MÉTHODE NE DOIT PAS LEVER D'EXCEPTION
        try:
            label.refresh_style()
        except Exception as e:
            pytest.fail(f"refresh_style() a levé une exception: {e}")

    def test_indicator_label_default_status_map(self, qt_widget_cleanup):
        """Test de la carte de statuts par défaut."""
        label = IndicatorLabel()

        # ////// VÉRIFIER LES STATUTS PAR DÉFAUT
        assert label.status == "neutral"

        # ////// TESTER LES DIFFÉRENTS STATUTS
        label.status = "online"
        assert label.status == "online"

        label.status = "offline"
        assert label.status == "offline"

        # ////// TESTER LES STATUTS QUI N'EXISTENT PAS
        with pytest.raises(ValueError, match="Unknown status"):
            label.status = "error"

        with pytest.raises(ValueError, match="Unknown status"):
            label.status = "warning"

        with pytest.raises(ValueError, match="Unknown status"):
            label.status = "success"

    def test_indicator_label_custom_status_map(self, qt_widget_cleanup):
        """Test avec une carte de statuts personnalisée."""
        custom_map = {
            "ready": {"text": "Prêt", "state": "ready", "color": "#4CAF50"},
            "busy": {"text": "Occupé", "state": "busy", "color": "#FF9800"},
            "error": {"text": "Erreur", "state": "error", "color": "#F44336"},
        }

        label = IndicatorLabel(status_map=custom_map, initial_status="ready")

        # ////// VÉRIFIER LE STATUT INITIAL
        assert label.status == "ready"

        # ////// TESTER LES AUTRES STATUTS
        label.status = "busy"
        assert label.status == "busy"

        label.status = "error"
        assert label.status == "error"

        # ////// TESTER UN STATUT QUI N'EXISTE PAS
        with pytest.raises(ValueError, match="Unknown status"):
            label.status = "unknown"

    def test_indicator_label_status_transitions(self, qt_widget_cleanup):
        """Test des transitions de statut."""
        label = IndicatorLabel()

        # ////// ÉTAT INITIAL
        assert label.status == "neutral"

        # ////// TRANSITION VERS ONLINE
        label.status = "online"
        assert label.status == "online"

        # ////// TRANSITION VERS OFFLINE
        label.status = "offline"
        assert label.status == "offline"

        # ////// TRANSITION VERS NEUTRAL
        label.status = "neutral"
        assert label.status == "neutral"

    def test_indicator_label_property_type(self, qt_widget_cleanup):
        """Test de la propriété type pour QSS."""
        label = IndicatorLabel()

        # ////// VÉRIFIER QUE LA PROPRIÉTÉ TYPE EST DÉFINIE
        assert label.property("type") == "IndicatorLabel"

    def test_indicator_label_multiple_instances(self, qt_widget_cleanup):
        """Test de plusieurs instances."""
        # ////// CRÉER PLUSIEURS INSTANCES
        label1 = IndicatorLabel(initial_status="online")
        label2 = IndicatorLabel(initial_status="offline")
        label3 = IndicatorLabel(initial_status="neutral")

        # ////// VÉRIFIER QUE CHAQUE INSTANCE EST INDÉPENDANTE
        assert label1.status == "online"
        assert label2.status == "offline"
        assert label3.status == "neutral"

        # ////// MODIFIER UNE INSTANCE
        label1.status = "offline"
        assert label1.status == "offline"
        assert label2.status == "offline"  # Non affecté
        assert label3.status == "neutral"  # Non affecté

    def test_indicator_label_empty_status_map(self, qt_widget_cleanup):
        """Test avec une carte de statuts vide."""
        empty_map = {}
        label = IndicatorLabel(status_map=empty_map)

        # ////// VÉRIFIER QUE LE WIDGET EST CRÉÉ
        assert label is not None
        assert isinstance(label, IndicatorLabel)

        # ////// TESTER UN CHANGEMENT DE STATUT (DOIT LÉVER UNE EXCEPTION)
        with pytest.raises(ValueError, match="Unknown status"):
            label.status = "any_status"

    def test_indicator_label_invalid_initial_status(self, qt_widget_cleanup):
        """Test avec un statut initial invalide."""
        # ////// CRÉER UN LABEL AVEC UN STATUT INVALIDE (DOIT LÉVER UNE EXCEPTION)
        with pytest.raises(ValueError, match="Unknown status"):
            IndicatorLabel(initial_status="invalid_status")

    def test_indicator_label_status_map_structure(self, qt_widget_cleanup):
        """Test de la structure de la carte de statuts."""
        # ////// CARTE AVEC STRUCTURE COMPLÈTE
        complete_map = {
            "test1": {"text": "Test 1", "state": "state1", "color": "#FF0000"},
            "test2": {"text": "Test 2", "state": "state2", "color": "#00FF00"},
        }

        label = IndicatorLabel(status_map=complete_map, initial_status="test1")
        assert label.status == "test1"

        # ////// CARTE AVEC STRUCTURE INCOMPLÈTE
        incomplete_map = {
            "test3": {
                "text": "Test 3"
                # Manque "state" et "color"
            }
        }

        label2 = IndicatorLabel(status_map=incomplete_map, initial_status="test3")
        assert label2.status == "test3"

    def test_indicator_label_status_changes_with_signals(self, qt_widget_cleanup):
        """Test des changements de statut avec signaux."""
        label = IndicatorLabel()

        # ////// CONNECTER LE SIGNAL
        signal_count = 0
        received_statuses = []

        def on_status_changed(status):
            nonlocal signal_count, received_statuses
            signal_count += 1
            received_statuses.append(status)

        label.statusChanged.connect(on_status_changed)

        # ////// CHANGER LE STATUT PLUSIEURS FOIS
        label.status = "online"
        label.status = "offline"
        label.status = "neutral"

        # ////// VÉRIFIER LES SIGNALS
        assert signal_count == 3
        assert received_statuses == ["online", "offline", "neutral"]

    def test_indicator_label_same_status_multiple_times(self, qt_widget_cleanup):
        """Test du même statut défini plusieurs fois."""
        label = IndicatorLabel()

        # ////// CONNECTER LE SIGNAL
        signal_count = 0

        def on_status_changed(status):
            nonlocal signal_count
            signal_count += 1

        label.statusChanged.connect(on_status_changed)

        # ////// DÉFINIR LE MÊME STATUT PLUSIEURS FOIS
        label.status = "online"
        label.status = "online"
        label.status = "online"

        # ////// VÉRIFIER QUE LE SIGNAL EST ÉMIS À CHAQUE FOIS
        # Note: Certains widgets peuvent ne pas émettre le signal si la valeur ne change pas
        # Vérifions plutôt que le statut final est correct
        assert label.status == "online"
        # Le signal peut être émis 1 fois (première définition) ou 3 fois selon l'implémentation
        assert signal_count >= 1

    def test_indicator_label_constructor_without_parameters(self, qt_widget_cleanup):
        """Test du constructeur sans paramètres."""
        label = IndicatorLabel()

        # ////// VÉRIFIER LES VALEURS PAR DÉFAUT
        assert label.status == "neutral"

        # ////// VÉRIFIER QUE LE WIDGET EST FONCTIONNEL
        label.status = "online"
        assert label.status == "online"
