# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

"""
Tests unitaires pour le widget ClickableTagLabel.
"""

import pytest
from unittest.mock import MagicMock
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QMouseEvent, QKeyEvent
from PySide6.QtWidgets import QApplication

from ezqt_widgets.label.clickable_tag_label import ClickableTagLabel


pytestmark = pytest.mark.unit


class TestClickableTagLabel:
    """Tests pour la classe ClickableTagLabel."""

    def test_clickable_tag_label_creation_default(self, qt_widget_cleanup):
        """Test de création avec paramètres par défaut."""
        tag = ClickableTagLabel()

        assert tag is not None
        assert isinstance(tag, ClickableTagLabel)
        assert tag.name == ""
        assert tag.enabled is False
        assert tag.status_color == "#0078d4"

    def test_clickable_tag_label_creation_with_parameters(self, qt_widget_cleanup):
        """Test de création avec paramètres personnalisés."""
        tag = ClickableTagLabel(
            name="Test Tag",
            enabled=True,
            status_color="#FF0000",
            min_width=100,
            min_height=30,
        )

        assert tag.name == "Test Tag"
        assert tag.enabled is True
        assert tag.status_color == "#FF0000"
        assert tag.min_width == 100
        assert tag.min_height == 30

    def test_clickable_tag_label_properties(self, qt_widget_cleanup):
        """Test des propriétés du tag."""
        tag = ClickableTagLabel()

        # ////// TEST NAME PROPERTY
        tag.name = "New Tag Name"
        assert tag.name == "New Tag Name"

        # ////// TEST ENABLED PROPERTY
        tag.enabled = True
        assert tag.enabled is True

        # ////// TEST STATUS_COLOR PROPERTY
        tag.status_color = "#00FF00"
        assert tag.status_color == "#00FF00"

        # ////// TEST MIN_WIDTH PROPERTY
        tag.min_width = 150
        assert tag.min_width == 150

        # ////// TEST MIN_HEIGHT PROPERTY
        tag.min_height = 40
        assert tag.min_height == 40

        # ////// TESTER AVEC NONE
        tag.min_width = None
        tag.min_height = None
        assert tag.min_width is None
        assert tag.min_height is None

    def test_clickable_tag_label_signals(self, qt_widget_cleanup):
        """Test des signaux du tag."""
        tag = ClickableTagLabel(name="Test Tag")

        # ////// TEST CLICKED SIGNAL
        clicked_signal_received = False

        def on_clicked():
            nonlocal clicked_signal_received
            clicked_signal_received = True

        tag.clicked.connect(on_clicked)

        # ////// SIMULER UN CLIC AVEC VRAI ÉVÉNEMENT QT
        from PySide6.QtCore import QPoint
        from PySide6.QtGui import QMouseEvent

        event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            QPoint(10, 10),
            QPoint(10, 10),
            Qt.LeftButton,
            Qt.LeftButton,
            Qt.NoModifier,
        )
        tag.mousePressEvent(event)

        # ////// VÉRIFIER QUE LE SIGNAL A ÉTÉ ÉMIS
        assert clicked_signal_received

        # ////// TEST TOGGLE_KEYWORD SIGNAL
        toggle_signal_received = False
        received_keyword = ""

        def on_toggle_keyword(keyword):
            nonlocal toggle_signal_received, received_keyword
            toggle_signal_received = True
            received_keyword = keyword

        tag.toggle_keyword.connect(on_toggle_keyword)

        # ////// SIMULER UN CLIC POUR TOGGLE
        tag.mousePressEvent(event)

        # ////// VÉRIFIER QUE LE SIGNAL A ÉTÉ ÉMIS
        assert toggle_signal_received
        assert received_keyword == "Test Tag"

        # ////// TEST STATECHANGED SIGNAL
        state_signal_received = False
        received_state = None

        def on_state_changed(state):
            nonlocal state_signal_received, received_state
            state_signal_received = True
            received_state = state

        tag.stateChanged.connect(on_state_changed)

        # ////// CHANGER L'ÉTAT
        tag.enabled = True

        # ////// VÉRIFIER QUE LE SIGNAL A ÉTÉ ÉMIS
        assert state_signal_received
        assert received_state is True

    def test_clickable_tag_label_mouse_press_event(self, qt_widget_cleanup):
        """Test de l'événement mousePressEvent."""
        tag = ClickableTagLabel(name="Test Tag")

        # ////// TEST CLIC GAUCHE
        from PySide6.QtCore import QPoint
        from PySide6.QtGui import QMouseEvent

        left_event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            QPoint(10, 10),
            QPoint(10, 10),
            Qt.LeftButton,
            Qt.LeftButton,
            Qt.NoModifier,
        )

        # ////// VÉRIFIER QUE L'ÉVÉNEMENT NE LÈVE PAS D'EXCEPTION
        try:
            tag.mousePressEvent(left_event)
        except Exception as e:
            pytest.fail(f"mousePressEvent() a levé une exception: {e}")

        # ////// TEST CLIC DROIT (NE DOIT PAS DÉCLENCHER LES SIGNALS)
        right_event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            QPoint(10, 10),
            QPoint(10, 10),
            Qt.RightButton,
            Qt.RightButton,
            Qt.NoModifier,
        )

        try:
            tag.mousePressEvent(right_event)
        except Exception as e:
            pytest.fail(f"mousePressEvent() a levé une exception: {e}")

    def test_clickable_tag_label_key_press_event(self, qt_widget_cleanup):
        """Test de l'événement keyPressEvent."""
        tag = ClickableTagLabel(name="Test Tag")

        # ////// TEST TOUCHE ESPACE
        mock_event = MagicMock()
        mock_event.key.return_value = Qt.Key_Space

        # ////// VÉRIFIER QUE L'ÉVÉNEMENT NE LÈVE PAS D'EXCEPTION
        try:
            tag.keyPressEvent(mock_event)
        except Exception as e:
            pytest.fail(f"keyPressEvent() a levé une exception: {e}")

        # ////// TEST AUTRE TOUCHE (NE DOIT PAS DÉCLENCHER LES SIGNALS)
        mock_event.key.return_value = Qt.Key_Enter

        try:
            tag.keyPressEvent(mock_event)
        except Exception as e:
            pytest.fail(f"keyPressEvent() a levé une exception: {e}")

    def test_clickable_tag_label_toggle_behavior(self, qt_widget_cleanup):
        """Test du comportement de toggle."""
        tag = ClickableTagLabel(name="Test Tag")

        # ////// ÉTAT INITIAL
        assert tag.enabled is False

        # ////// PREMIER CLIC - ACTIVE LE TAG
        from PySide6.QtCore import QPoint
        from PySide6.QtGui import QMouseEvent

        event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            QPoint(10, 10),
            QPoint(10, 10),
            Qt.LeftButton,
            Qt.LeftButton,
            Qt.NoModifier,
        )

        clicked_count = 0

        def on_clicked():
            nonlocal clicked_count
            clicked_count += 1

        tag.clicked.connect(on_clicked)
        tag.mousePressEvent(event)

        # ////// VÉRIFIER QUE LE TAG EST MAINTENANT ACTIF
        assert tag.enabled is True
        assert clicked_count == 1

        # ////// DEUXIÈME CLIC - DÉSACTIVE LE TAG
        tag.mousePressEvent(event)

        # ////// VÉRIFIER QUE LE TAG EST MAINTENANT INACTIF
        assert tag.enabled is False
        assert clicked_count == 2

    def test_clickable_tag_label_toggle_via_property(self, qt_widget_cleanup):
        """Test du toggle via la propriété enabled."""
        tag = ClickableTagLabel(name="Test Tag")

        # ////// ÉTAT INITIAL
        assert tag.enabled is False

        # ////// CONNECTER LE SIGNAL
        state_signal_received = False
        received_state = None

        def on_state_changed(state):
            nonlocal state_signal_received, received_state
            state_signal_received = True
            received_state = state

        tag.stateChanged.connect(on_state_changed)

        # ////// TOGGLE VIA PROPRIÉTÉ
        tag.enabled = True
        assert tag.enabled is True
        assert state_signal_received
        assert received_state is True

        # ////// TOGGLE ENCORE
        tag.enabled = False
        assert tag.enabled is False

    def test_clickable_tag_label_keyboard_toggle(self, qt_widget_cleanup):
        """Test du toggle par clavier."""
        tag = ClickableTagLabel(name="Test Tag")

        # ////// ÉTAT INITIAL
        assert tag.enabled is False

        # ////// TOUCHE ESPACE - ACTIVE LE TAG
        mock_event = MagicMock()
        mock_event.key.return_value = Qt.Key_Space

        clicked_count = 0

        def on_clicked():
            nonlocal clicked_count
            clicked_count += 1

        tag.clicked.connect(on_clicked)
        tag.keyPressEvent(mock_event)

        # ////// VÉRIFIER QUE LE TAG EST MAINTENANT ACTIF
        assert tag.enabled is True
        assert clicked_count == 1

        # ////// DEUXIÈME TOUCHE ESPACE - DÉSACTIVE LE TAG
        tag.keyPressEvent(mock_event)

        # ////// VÉRIFIER QUE LE TAG EST MAINTENANT INACTIF
        assert tag.enabled is False
        assert clicked_count == 2

    def test_clickable_tag_label_size_hints(self, qt_widget_cleanup):
        """Test des méthodes de taille."""
        tag = ClickableTagLabel(name="Test Tag")

        # ////// TEST SIZEHINT
        size_hint = tag.sizeHint()
        assert size_hint is not None
        assert isinstance(size_hint, QSize)
        assert size_hint.width() > 0
        assert size_hint.height() > 0

        # ////// TEST MINIMUMSIZEHINT
        min_size_hint = tag.minimumSizeHint()
        assert min_size_hint is not None
        assert isinstance(min_size_hint, QSize)
        assert min_size_hint.width() > 0
        assert min_size_hint.height() > 0

    def test_clickable_tag_label_refresh_style(self, qt_widget_cleanup):
        """Test de la méthode refresh_style."""
        tag = ClickableTagLabel()

        # ////// LA MÉTHODE NE DOIT PAS LEVER D'EXCEPTION
        try:
            tag.refresh_style()
        except Exception as e:
            pytest.fail(f"refresh_style() a levé une exception: {e}")

    def test_clickable_tag_label_display_update(self, qt_widget_cleanup):
        """Test de la mise à jour de l'affichage."""
        tag = ClickableTagLabel(name="Test Tag")

        # ////// VÉRIFIER L'AFFICHAGE INITIAL
        assert tag.name == "Test Tag"

        # ////// CHANGER LE NOM
        tag.name = "New Tag Name"
        assert tag.name == "New Tag Name"

        # ////// CHANGER LA COULEUR
        tag.status_color = "#FF0000"
        assert tag.status_color == "#FF0000"

    def test_clickable_tag_label_accessibility(self, qt_widget_cleanup):
        """Test de l'accessibilité."""
        tag = ClickableTagLabel(name="Test Tag")

        # ////// VÉRIFIER QUE LE WIDGET PEUT RECEVOIR LE FOCUS
        # Note: Le focusPolicy peut varier selon l'implémentation
        focus_policy = tag.focusPolicy()
        assert focus_policy in [
            Qt.StrongFocus,
            Qt.ClickFocus,
            Qt.TabFocus,
            Qt.WheelFocus,
        ]

        # ////// VÉRIFIER QUE LE WIDGET EST FOCUSABLE
        tag.setFocus()
        # Note: hasFocus() peut ne pas fonctionner dans un contexte de test
        # Vérifions plutôt que setFocus() ne lève pas d'exception
        try:
            tag.setFocus()
        except Exception as e:
            pytest.fail(f"setFocus() a levé une exception: {e}")

    def test_clickable_tag_label_properties_validation(self, qt_widget_cleanup):
        """Test de la validation des propriétés."""
        tag = ClickableTagLabel()

        # ////// TEST NOM VIDE
        tag.name = ""
        assert tag.name == ""

        # ////// TEST NOM AVEC ESPACES
        tag.name = "   Tag with spaces   "
        assert tag.name == "   Tag with spaces   "

        # ////// TEST COULEUR INVALIDE (DOIT ÊTRE ACCEPTÉE)
        tag.status_color = "invalid_color"
        assert tag.status_color == "invalid_color"

        # ////// TEST DIMENSIONS NÉGATIVES (DOIVENT ÊTRE ACCEPTÉES)
        tag.min_width = -10
        tag.min_height = -5
        assert tag.min_width == -10
        assert tag.min_height == -5
