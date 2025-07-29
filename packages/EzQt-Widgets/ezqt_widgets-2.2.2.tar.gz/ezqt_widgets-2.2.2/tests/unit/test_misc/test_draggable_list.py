#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests unitaires pour le widget DraggableList.

Ce module contient tous les tests nécessaires pour valider le bon fonctionnement
du widget DraggableList et de ses composants DraggableItem.
"""

import pytest
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QMouseEvent, QDragEnterEvent, QDropEvent, QMimeData
from PySide6.QtWidgets import QApplication

from ezqt_widgets.misc.draggable_list import DraggableList, DraggableItem


@pytest.fixture
def app():
    """Fixture pour créer une application Qt."""
    return QApplication([])


@pytest.fixture
def draggable_list(app):
    """Fixture pour créer une DraggableList de test."""
    return DraggableList(
        items=["Item 1", "Item 2", "Item 3"],
        allow_drag_drop=True,
        allow_remove=True,
        max_height=300,
        min_width=150,
        compact=False,
    )


@pytest.fixture
def compact_draggable_list(app):
    """Fixture pour créer une DraggableList compacte de test."""
    return DraggableList(
        items=["Option A", "Option B"],
        compact=True,
        allow_drag_drop=True,
        allow_remove=True,
    )


@pytest.fixture
def draggable_item(app):
    """Fixture pour créer un DraggableItem de test."""
    return DraggableItem(item_id="test_item", text="Test Item", compact=False)


class TestDraggableItem:
    """Tests pour la classe DraggableItem."""

    def test_init(self, draggable_item):
        """Test de l'initialisation d'un DraggableItem."""
        assert draggable_item.item_id == "test_item"
        assert draggable_item.text == "Test Item"
        assert draggable_item.is_dragging is False
        assert draggable_item._compact is False
        assert draggable_item._icon_color == "grey"

    def test_init_compact(self, app):
        """Test de l'initialisation d'un DraggableItem en mode compact."""
        item = DraggableItem(item_id="compact_item", text="Compact Item", compact=True)
        assert item._compact is True
        assert item.minimumHeight() == 24
        assert item.maximumHeight() == 32

    def test_icon_color_property(self, draggable_item):
        """Test de la propriété icon_color."""
        draggable_item.icon_color = "red"
        assert draggable_item.icon_color == "red"
        assert draggable_item.content_widget.icon_color == "red"

    def test_compact_property(self, draggable_item):
        """Test de la propriété compact."""
        # Mode normal
        assert draggable_item.compact is False
        assert draggable_item.minimumHeight() == 40
        assert draggable_item.maximumHeight() == 60

        # Mode compact
        draggable_item.compact = True
        assert draggable_item.compact is True
        assert draggable_item.minimumHeight() == 24
        assert draggable_item.maximumHeight() == 32

    def test_size_hint(self, draggable_item):
        """Test du calcul de sizeHint."""
        size = draggable_item.sizeHint()
        assert size.width() > 0
        assert 40 <= size.height() <= 60

    def test_size_hint_compact(self, app):
        """Test du calcul de sizeHint en mode compact."""
        item = DraggableItem(item_id="compact_item", text="Compact Item", compact=True)
        size = item.sizeHint()
        assert size.width() > 0
        assert 24 <= size.height() <= 32

    def test_minimum_size_hint(self, draggable_item):
        """Test du calcul de minimumSizeHint."""
        size = draggable_item.minimumSizeHint()
        assert size.width() > 0
        assert size.height() == 40

    def test_minimum_size_hint_compact(self, app):
        """Test du calcul de minimumSizeHint en mode compact."""
        item = DraggableItem(item_id="compact_item", text="Compact Item", compact=True)
        size = item.minimumSizeHint()
        assert size.width() > 0
        assert size.height() == 24

    def test_mouse_press_event(self, draggable_item):
        """Test de l'événement mousePressEvent."""
        # Simuler un clic gauche
        event = QMouseEvent(
            QMouseEvent.MouseButtonPress,
            QPoint(10, 10),
            Qt.LeftButton,
            Qt.LeftButton,
            Qt.NoModifier,
        )
        draggable_item.mousePressEvent(event)
        assert draggable_item.drag_start_pos == QPoint(10, 10)

    def test_on_remove_clicked(self, draggable_item):
        """Test du signal itemRemoved."""
        # Connecter un callback pour vérifier l'émission du signal
        called = False

        def callback(item_id):
            nonlocal called
            called = True
            assert item_id == "test_item"

        draggable_item.itemRemoved.connect(callback)
        draggable_item._on_remove_clicked()
        assert called is True

    def test_refresh_style(self, draggable_item):
        """Test de la méthode refresh_style."""
        # Cette méthode ne devrait pas lever d'exception
        draggable_item.refresh_style()


class TestDraggableList:
    """Tests pour la classe DraggableList."""

    def test_init(self, draggable_list):
        """Test de l'initialisation d'une DraggableList."""
        assert draggable_list._items == ["Item 1", "Item 2", "Item 3"]
        assert draggable_list._allow_drag_drop is True
        assert draggable_list._allow_remove is True
        assert draggable_list._max_height == 300
        assert draggable_list._min_width == 150
        assert draggable_list._compact is False
        assert draggable_list._icon_color == "grey"
        assert len(draggable_list._item_widgets) == 3

    def test_init_compact(self, compact_draggable_list):
        """Test de l'initialisation d'une DraggableList compacte."""
        assert compact_draggable_list._compact is True
        assert compact_draggable_list._items == ["Option A", "Option B"]
        assert len(compact_draggable_list._item_widgets) == 2

    def test_items_property(self, draggable_list):
        """Test de la propriété items."""
        # Getter
        items = draggable_list.items
        assert items == ["Item 1", "Item 2", "Item 3"]
        assert items is not draggable_list._items  # Copie

        # Setter
        new_items = ["New 1", "New 2"]
        draggable_list.items = new_items
        assert draggable_list._items == new_items
        assert len(draggable_list._item_widgets) == 2

    def test_item_count_property(self, draggable_list):
        """Test de la propriété item_count."""
        assert draggable_list.item_count == 3

    def test_allow_drag_drop_property(self, draggable_list):
        """Test de la propriété allow_drag_drop."""
        assert draggable_list.allow_drag_drop is True

        draggable_list.allow_drag_drop = False
        assert draggable_list.allow_drag_drop is False

    def test_allow_remove_property(self, draggable_list):
        """Test de la propriété allow_remove."""
        assert draggable_list.allow_remove is True

        draggable_list.allow_remove = False
        assert draggable_list.allow_remove is False

        # Vérifier que l'icône de suppression est désactivée
        for widget in draggable_list._item_widgets.values():
            assert widget.content_widget.icon_enabled is False

    def test_icon_color_property(self, draggable_list):
        """Test de la propriété icon_color."""
        assert draggable_list.icon_color == "grey"

        draggable_list.icon_color = "red"
        assert draggable_list.icon_color == "red"

        # Vérifier que tous les éléments ont la nouvelle couleur
        for widget in draggable_list._item_widgets.values():
            assert widget.icon_color == "red"

    def test_compact_property(self, draggable_list):
        """Test de la propriété compact."""
        assert draggable_list.compact is False

        draggable_list.compact = True
        assert draggable_list.compact is True

        # Vérifier que tous les éléments sont en mode compact
        for widget in draggable_list._item_widgets.values():
            assert widget.compact is True

    def test_min_width_property(self, draggable_list):
        """Test de la propriété min_width."""
        assert draggable_list.min_width == 150

        draggable_list.min_width = 200
        assert draggable_list.min_width == 200

    def test_add_item(self, draggable_list):
        """Test de l'ajout d'un élément."""
        initial_count = draggable_list.item_count

        # Connecter un callback pour vérifier l'émission du signal
        called = False

        def callback(item_id, position):
            nonlocal called
            called = True
            assert item_id == "new_item"
            assert position == initial_count

        draggable_list.itemAdded.connect(callback)

        draggable_list.add_item("new_item", "New Item")

        assert draggable_list.item_count == initial_count + 1
        assert "new_item" in draggable_list._items
        assert "new_item" in draggable_list._item_widgets
        assert called is True

    def test_add_item_duplicate(self, draggable_list):
        """Test de l'ajout d'un élément déjà présent."""
        initial_count = draggable_list.item_count
        draggable_list.add_item("Item 1", "Item 1")  # Déjà présent
        assert draggable_list.item_count == initial_count  # Pas d'ajout

    def test_remove_item(self, draggable_list):
        """Test de la suppression d'un élément."""
        initial_count = draggable_list.item_count

        # Connecter un callback pour vérifier l'émission du signal
        called = False

        def callback(item_id, position):
            nonlocal called
            called = True
            assert item_id == "Item 2"
            assert position == 1

        draggable_list.itemRemoved.connect(callback)

        result = draggable_list.remove_item("Item 2")

        assert result is True
        assert draggable_list.item_count == initial_count - 1
        assert "Item 2" not in draggable_list._items
        assert "Item 2" not in draggable_list._item_widgets
        assert called is True

    def test_remove_item_not_found(self, draggable_list):
        """Test de la suppression d'un élément inexistant."""
        initial_count = draggable_list.item_count
        result = draggable_list.remove_item("inexistant")
        assert result is False
        assert draggable_list.item_count == initial_count

    def test_clear_items(self, draggable_list):
        """Test du vidage de la liste."""
        assert draggable_list.item_count > 0

        # Connecter un callback pour vérifier l'émission du signal
        called = False

        def callback(new_order):
            nonlocal called
            called = True
            assert new_order == []

        draggable_list.orderChanged.connect(callback)

        draggable_list.clear_items()

        assert draggable_list.item_count == 0
        assert len(draggable_list._items) == 0
        assert len(draggable_list._item_widgets) == 0
        assert called is True

    def test_move_item(self, draggable_list):
        """Test du déplacement d'un élément."""
        # Connecter un callback pour vérifier l'émission du signal
        called = False

        def callback(item_id, old_pos, new_pos):
            nonlocal called
            called = True
            assert item_id == "Item 1"
            assert old_pos == 0
            assert new_pos == 2

        draggable_list.itemMoved.connect(callback)

        result = draggable_list.move_item("Item 1", 2)

        assert result is True
        assert draggable_list._items == ["Item 2", "Item 3", "Item 1"]
        assert called is True

    def test_move_item_same_position(self, draggable_list):
        """Test du déplacement d'un élément à la même position."""
        original_items = draggable_list._items.copy()
        result = draggable_list.move_item("Item 1", 0)
        assert result is True
        assert draggable_list._items == original_items

    def test_move_item_not_found(self, draggable_list):
        """Test du déplacement d'un élément inexistant."""
        result = draggable_list.move_item("inexistant", 1)
        assert result is False

    def test_get_item_position(self, draggable_list):
        """Test de l'obtention de la position d'un élément."""
        position = draggable_list.get_item_position("Item 2")
        assert position == 1

    def test_get_item_position_not_found(self, draggable_list):
        """Test de l'obtention de la position d'un élément inexistant."""
        position = draggable_list.get_item_position("inexistant")
        assert position == -1

    def test_size_hint(self, draggable_list):
        """Test du calcul de sizeHint."""
        size = draggable_list.sizeHint()
        assert size.width() >= draggable_list._min_width
        assert size.height() > 0

    def test_minimum_size_hint(self, draggable_list):
        """Test du calcul de minimumSizeHint."""
        size = draggable_list.minimumSizeHint()
        assert size.width() >= draggable_list._min_width
        assert size.height() > 0

    def test_drag_enter_event(self, draggable_list):
        """Test de l'événement dragEnterEvent."""
        mime_data = QMimeData()
        mime_data.setText("Item 1")
        event = QDragEnterEvent(
            QPoint(10, 10), Qt.MoveAction, mime_data, Qt.LeftButton, Qt.NoModifier
        )

        # Avec drag & drop activé
        draggable_list.allow_drag_drop = True
        draggable_list.dragEnterEvent(event)
        assert event.isAccepted()

        # Avec drag & drop désactivé
        draggable_list.allow_drag_drop = False
        event = QDragEnterEvent(
            QPoint(10, 10), Qt.MoveAction, mime_data, Qt.LeftButton, Qt.NoModifier
        )
        draggable_list.dragEnterEvent(event)
        assert not event.isAccepted()

    def test_drag_move_event(self, draggable_list):
        """Test de l'événement dragMoveEvent."""
        mime_data = QMimeData()
        mime_data.setText("Item 1")
        event = QDragMoveEvent(
            QPoint(10, 10), Qt.MoveAction, mime_data, Qt.LeftButton, Qt.NoModifier
        )

        # Avec drag & drop activé
        draggable_list.allow_drag_drop = True
        draggable_list.dragMoveEvent(event)
        assert event.isAccepted()

        # Avec drag & drop désactivé
        draggable_list.allow_drag_drop = False
        event = QDragMoveEvent(
            QPoint(10, 10), Qt.MoveAction, mime_data, Qt.LeftButton, Qt.NoModifier
        )
        draggable_list.dragMoveEvent(event)
        assert not event.isAccepted()

    def test_drop_event(self, draggable_list):
        """Test de l'événement dropEvent."""
        mime_data = QMimeData()
        mime_data.setText("Item 1")
        event = QDropEvent(
            QPoint(10, 10), Qt.MoveAction, mime_data, Qt.LeftButton, Qt.NoModifier
        )

        # Avec drag & drop activé et élément valide
        draggable_list.allow_drag_drop = True
        draggable_list.dropEvent(event)
        assert event.isAccepted()

        # Avec élément inexistant
        mime_data.setText("inexistant")
        event = QDropEvent(
            QPoint(10, 10), Qt.MoveAction, mime_data, Qt.LeftButton, Qt.NoModifier
        )
        draggable_list.dropEvent(event)
        assert not event.isAccepted()

    def test_calculate_drop_position(self, draggable_list):
        """Test du calcul de la position de drop."""
        # Test avec une position en haut
        drop_pos = QPoint(10, 5)
        position = draggable_list._calculate_drop_position(drop_pos)
        assert position == 0

        # Test avec une position en bas
        drop_pos = QPoint(10, 1000)
        position = draggable_list._calculate_drop_position(drop_pos)
        assert position == 2  # len(items) - 1

    def test_refresh_style(self, draggable_list):
        """Test de la méthode refresh_style."""
        # Cette méthode ne devrait pas lever d'exception
        draggable_list.refresh_style()

    def test_on_item_removed(self, draggable_list):
        """Test du callback on_item_removed."""
        # Simuler la suppression d'un élément via le signal
        draggable_list._on_item_removed("Item 1")
        assert "Item 1" not in draggable_list._items


class TestDraggableListIntegration:
    """Tests d'intégration pour DraggableList."""

    def test_signal_chain(self, draggable_list):
        """Test de la chaîne de signaux lors d'opérations."""
        signals_received = []

        def on_item_moved(item_id, old_pos, new_pos):
            signals_received.append(("moved", item_id, old_pos, new_pos))

        def on_order_changed(new_order):
            signals_received.append(("order_changed", new_order))

        draggable_list.itemMoved.connect(on_item_moved)
        draggable_list.orderChanged.connect(on_order_changed)

        # Déplacer un élément
        draggable_list.move_item("Item 1", 2)

        assert len(signals_received) == 2
        assert signals_received[0][0] == "moved"
        assert signals_received[1][0] == "order_changed"

    def test_compact_mode_switch(self, draggable_list):
        """Test du changement de mode compact."""
        # Vérifier l'état initial
        assert draggable_list.compact is False
        for widget in draggable_list._item_widgets.values():
            assert widget.compact is False

        # Passer en mode compact
        draggable_list.compact = True
        assert draggable_list.compact is True
        for widget in draggable_list._item_widgets.values():
            assert widget.compact is True

    def test_icon_color_propagation(self, draggable_list):
        """Test de la propagation de la couleur d'icône."""
        # Changer la couleur
        draggable_list.icon_color = "blue"

        # Vérifier que tous les éléments ont la nouvelle couleur
        for widget in draggable_list._item_widgets.values():
            assert widget.icon_color == "blue"

    def test_allow_remove_propagation(self, draggable_list):
        """Test de la propagation de allow_remove."""
        # Désactiver la suppression
        draggable_list.allow_remove = False

        # Vérifier que tous les éléments ont la suppression désactivée
        for widget in draggable_list._item_widgets.values():
            assert widget.content_widget.icon_enabled is False


if __name__ == "__main__":
    pytest.main([__file__])
