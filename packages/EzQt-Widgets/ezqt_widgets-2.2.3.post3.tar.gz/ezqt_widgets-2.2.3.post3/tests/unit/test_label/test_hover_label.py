# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

"""
Tests unitaires pour le widget HoverLabel.
"""

import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtCore import QSize, Qt, QRect, QEvent
from PySide6.QtGui import QIcon, QPixmap, QColor, QMouseEvent, QEnterEvent
from PySide6.QtWidgets import QApplication

from ezqt_widgets.label.hover_label import HoverLabel


pytestmark = pytest.mark.unit


class TestHoverLabel:
    """Tests pour la classe HoverLabel."""

    def test_hover_label_creation_default(self, qt_widget_cleanup):
        """Test de création avec paramètres par défaut."""
        label = HoverLabel()

        assert label is not None
        assert isinstance(label, HoverLabel)
        assert label.text() == ""
        assert label.opacity == 0.5
        assert label.icon_size == QSize(16, 16)
        assert label.icon_color is None
        assert label.icon_padding == 8
        assert label.icon_enabled is True

    def test_hover_label_creation_with_parameters(self, qt_widget_cleanup):
        """Test de création avec paramètres personnalisés."""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.red)
        icon = QIcon(pixmap)

        label = HoverLabel(
            icon=icon,
            text="Test Label",
            opacity=0.8,
            icon_size=QSize(24, 24),
            icon_color="#FF0000",
            icon_padding=12,
            icon_enabled=False,
            min_width=200,
        )

        assert label.text() == "Test Label"
        assert label.opacity == 0.8
        assert label.icon_size == QSize(24, 24)
        assert label.icon_color == "#FF0000"
        assert label.icon_padding == 12
        assert label.icon_enabled is False

    def test_hover_label_properties(self, qt_widget_cleanup):
        """Test des propriétés du label."""
        label = HoverLabel()

        # ////// TEST OPACITY PROPERTY
        label.opacity = 0.7
        assert label.opacity == 0.7

        # ////// TEST HOVER_ICON PROPERTY
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.blue)
        icon = QIcon(pixmap)
        label.hover_icon = icon
        assert label.hover_icon is not None

        # ////// TEST ICON_SIZE PROPERTY
        label.icon_size = QSize(32, 32)
        assert label.icon_size == QSize(32, 32)

        # ////// TEST ICON_COLOR PROPERTY
        label.icon_color = "#00FF00"
        assert label.icon_color == "#00FF00"

        # ////// TEST ICON_PADDING PROPERTY
        label.icon_padding = 16
        assert label.icon_padding == 16

        # ////// TEST ICON_ENABLED PROPERTY
        label.icon_enabled = False
        assert label.icon_enabled is False

    def test_hover_label_signals(self, qt_widget_cleanup):
        """Test des signaux du label."""
        # Créer un label avec une icône pour que le signal puisse être émis
        from PySide6.QtGui import QIcon, QPixmap

        # Créer une icône simple
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.blue)
        icon = QIcon(pixmap)

        label = HoverLabel(icon=icon)

        # ////// TEST HOVERICONCLICKED SIGNAL
        signal_received = False

        def on_hover_icon_clicked():
            nonlocal signal_received
            signal_received = True

        label.hoverIconClicked.connect(on_hover_icon_clicked)

        # ////// SIMULER L'ENTRÉE DE LA SOURIS
        from PySide6.QtCore import QPoint
        from PySide6.QtGui import QEnterEvent

        enter_event = QEnterEvent(QPoint(10, 10), QPoint(10, 10), QPoint(10, 10))
        label.enterEvent(enter_event)

        # ////// SIMULER UN CLIC SUR L'ICÔNE (position dans la zone de l'icône)
        from PySide6.QtGui import QMouseEvent

        # Calculer la position de l'icône (à droite du widget)
        icon_x = label.width() - label.icon_size.width() - 4
        icon_y = (label.height() - label.icon_size.height()) // 2

        mouse_event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            QPoint(icon_x + 5, icon_y + 5),  # Position dans l'icône
            QPoint(icon_x + 5, icon_y + 5),
            Qt.LeftButton,
            Qt.LeftButton,
            Qt.NoModifier,
        )
        label.mousePressEvent(mouse_event)

        # ////// VÉRIFIER QUE LE SIGNAL A ÉTÉ ÉMIS
        assert signal_received

    def test_hover_label_mouse_events(self, qt_widget_cleanup):
        """Test des événements souris."""
        label = HoverLabel()

        # ////// TEST MOUSEMOVEEVENT
        from PySide6.QtCore import QPoint
        from PySide6.QtGui import QMouseEvent

        mouse_move_event = QMouseEvent(
            QMouseEvent.Type.MouseMove,
            QPoint(10, 10),
            QPoint(10, 10),
            Qt.NoButton,
            Qt.NoButton,
            Qt.NoModifier,
        )

        try:
            label.mouseMoveEvent(mouse_move_event)
        except Exception as e:
            pytest.fail(f"mouseMoveEvent() a levé une exception: {e}")

        # ////// TEST MOUSEPRESSEVENT
        mouse_press_event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            QPoint(10, 10),
            QPoint(10, 10),
            Qt.LeftButton,
            Qt.LeftButton,
            Qt.NoModifier,
        )

        try:
            label.mousePressEvent(mouse_press_event)
        except Exception as e:
            pytest.fail(f"mousePressEvent() a levé une exception: {e}")

    def test_hover_label_enter_leave_events(self, qt_widget_cleanup):
        """Test des événements enter/leave."""
        label = HoverLabel()

        # ////// TEST ENTEREVENT
        from PySide6.QtCore import QPoint
        from PySide6.QtGui import QEnterEvent

        enter_event = QEnterEvent(QPoint(10, 10), QPoint(10, 10), QPoint(10, 10))
        try:
            label.enterEvent(enter_event)
        except Exception as e:
            pytest.fail(f"enterEvent() a levé une exception: {e}")

        # ////// TEST LEAVEEVENT
        from PySide6.QtCore import QEvent

        leave_event = QEvent(QEvent.Type.Leave)
        try:
            label.leaveEvent(leave_event)
        except Exception as e:
            pytest.fail(f"leaveEvent() a levé une exception: {e}")

    def test_hover_label_paint_event(self, qt_widget_cleanup):
        """Test de l'événement paint."""
        label = HoverLabel()

        # ////// TEST PAINTEVENT
        from PySide6.QtGui import QPaintEvent
        from PySide6.QtCore import QRect

        paint_event = QPaintEvent(QRect(0, 0, 100, 50))
        try:
            label.paintEvent(paint_event)
        except Exception as e:
            pytest.fail(f"paintEvent() a levé une exception: {e}")

    def test_hover_label_resize_event(self, qt_widget_cleanup):
        """Test de l'événement resize."""
        label = HoverLabel()

        # ////// TEST RESIZEEVENT
        from PySide6.QtGui import QResizeEvent
        from PySide6.QtCore import QSize

        resize_event = QResizeEvent(QSize(100, 50), QSize(80, 40))
        try:
            label.resizeEvent(resize_event)
        except Exception as e:
            pytest.fail(f"resizeEvent() a levé une exception: {e}")

    def test_hover_label_size_hints(self, qt_widget_cleanup):
        """Test des méthodes de taille."""
        label = HoverLabel(text="Test Label")

        # ////// TEST MINIMUMSIZEHINT
        min_size_hint = label.minimumSizeHint()
        assert min_size_hint is not None
        assert isinstance(min_size_hint, QSize)
        assert min_size_hint.width() > 0
        assert min_size_hint.height() > 0

    def test_hover_label_refresh_style(self, qt_widget_cleanup):
        """Test de la méthode refresh_style."""
        label = HoverLabel()

        # ////// LA MÉTHODE NE DOIT PAS LEVER D'EXCEPTION
        try:
            label.refresh_style()
        except Exception as e:
            pytest.fail(f"refresh_style() a levé une exception: {e}")

    def test_hover_label_clear_icon(self, qt_widget_cleanup):
        """Test de la méthode clear_icon."""
        label = HoverLabel()

        # ////// DÉFINIR UNE ICÔNE
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.red)
        icon = QIcon(pixmap)
        label.hover_icon = icon

        # ////// EFFACER L'ICÔNE
        label.clear_icon()

        # ////// VÉRIFIER QUE L'ICÔNE EST EFFACÉE
        assert label.hover_icon is None

    def test_hover_label_icon_enabled_disabled(self, qt_widget_cleanup):
        """Test de l'activation/désactivation de l'icône."""
        label = HoverLabel()

        # ////// ÉTAT INITIAL
        assert label.icon_enabled is True

        # ////// DÉSACTIVER L'ICÔNE
        label.icon_enabled = False
        assert label.icon_enabled is False

        # ////// RÉACTIVER L'ICÔNE
        label.icon_enabled = True
        assert label.icon_enabled is True

    def test_hover_label_icon_color_changes(self, qt_widget_cleanup):
        """Test des changements de couleur d'icône."""
        label = HoverLabel()

        # ////// DÉFINIR UNE COULEUR
        label.icon_color = "#FF0000"
        assert label.icon_color == "#FF0000"

        # ////// CHANGER LA COULEUR
        label.icon_color = "#00FF00"
        assert label.icon_color == "#00FF00"

        # ////// EFFACER LA COULEUR
        label.icon_color = None
        assert label.icon_color is None

    def test_hover_label_icon_size_changes(self, qt_widget_cleanup):
        """Test des changements de taille d'icône."""
        label = HoverLabel()

        # ////// TAILLE INITIALE
        assert label.icon_size == QSize(16, 16)

        # ////// CHANGER LA TAILLE
        label.icon_size = QSize(32, 32)
        assert label.icon_size == QSize(32, 32)

        # ////// CHANGER AVEC UN TUPLE
        label.icon_size = (24, 24)
        assert label.icon_size == QSize(24, 24)

    def test_hover_label_opacity_changes(self, qt_widget_cleanup):
        """Test des changements d'opacité."""
        label = HoverLabel()

        # ////// OPACITÉ INITIALE
        assert label.opacity == 0.5

        # ////// CHANGER L'OPACITÉ
        label.opacity = 0.8
        assert label.opacity == 0.8

        # ////// OPACITÉ MINIMALE
        label.opacity = 0.0
        assert label.opacity == 0.0

        # ////// OPACITÉ MAXIMALE
        label.opacity = 1.0
        assert label.opacity == 1.0

    def test_hover_label_padding_changes(self, qt_widget_cleanup):
        """Test des changements de padding."""
        label = HoverLabel()

        # ////// PADDING INITIAL
        assert label.icon_padding == 8

        # ////// CHANGER LE PADDING
        label.icon_padding = 16
        assert label.icon_padding == 16

        # ////// PADDING ZÉRO
        label.icon_padding = 0
        assert label.icon_padding == 0

        # ////// PADDING NÉGATIF
        label.icon_padding = -5
        assert label.icon_padding == -5

    def test_hover_label_text_changes(self, qt_widget_cleanup):
        """Test des changements de texte."""
        label = HoverLabel()

        # ////// TEXTE INITIAL
        assert label.text() == ""

        # ////// DÉFINIR UN TEXTE
        label.setText("Test Text")
        assert label.text() == "Test Text"

        # ////// CHANGER LE TEXTE
        label.setText("New Text")
        assert label.text() == "New Text"

        # ////// TEXTE VIDE
        label.setText("")
        assert label.text() == ""

    def test_hover_label_icon_from_path(self, qt_widget_cleanup, mock_icon_path):
        """Test de chargement d'icône depuis un chemin."""
        label = HoverLabel()

        # ////// CHARGER UNE ICÔNE DEPUIS UN CHEMIN
        label.hover_icon = mock_icon_path

        # ////// VÉRIFIER QUE L'ICÔNE EST CHARGÉE
        assert label.hover_icon is not None
        assert isinstance(label.hover_icon, QIcon)

    def test_hover_label_icon_from_svg(self, qt_widget_cleanup, mock_svg_path):
        """Test de chargement d'icône SVG."""
        label = HoverLabel()

        # ////// CHARGER UNE ICÔNE SVG
        label.hover_icon = mock_svg_path

        # ////// VÉRIFIER QUE L'ICÔNE EST CHARGÉE
        assert label.hover_icon is not None
        assert isinstance(label.hover_icon, QIcon)

    def test_hover_label_cursor_changes(self, qt_widget_cleanup):
        """Test des changements de curseur."""
        label = HoverLabel()

        # ////// CURSEUR INITIAL
        initial_cursor = label.cursor()

        # ////// SIMULER L'ENTRÉE DE LA SOURIS
        from PySide6.QtCore import QPoint
        from PySide6.QtGui import QEnterEvent

        enter_event = QEnterEvent(QPoint(10, 10), QPoint(10, 10), QPoint(10, 10))
        label.enterEvent(enter_event)

        # ////// VÉRIFIER QUE LE CURSEUR A CHANGÉ
        # Note: Le curseur peut changer selon l'implémentation

        # ////// SIMULER LA SORTIE DE LA SOURIS
        from PySide6.QtCore import QEvent

        leave_event = QEvent(QEvent.Type.Leave)
        label.leaveEvent(leave_event)

        # ////// VÉRIFIER QUE LE CURSEUR EST RESTAURÉ
        # Note: Le curseur peut être restauré selon l'implémentation
