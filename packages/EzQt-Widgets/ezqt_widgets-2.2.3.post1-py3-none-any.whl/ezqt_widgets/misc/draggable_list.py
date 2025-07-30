# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

# IMPORT BASE
# ///////////////////////////////////////////////////////////////

from PySide6.QtCore import (
    QPoint,
    QSize,
    Signal,
    Qt,
    QMimeData,
)
from PySide6.QtGui import (
    QDrag,
    QDragEnterEvent,
    QDragMoveEvent,
    QDropEvent,
    QMouseEvent,
)
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from ..label.hover_label import HoverLabel

# ////// TYPE HINTS IMPROVEMENTS FOR PYSIDE6 6.9.1
from typing import Any, Dict, List, Optional, Union

# UTILITY FUNCTIONS
# ///////////////////////////////////////////////////////////////


class DraggableItem(QFrame):
    """
    Widget d'élément draggable pour DraggableList.

    Cet élément peut être déplacé par drag & drop et contient
    toujours un HoverLabel pour une interface cohérente.
    """

    itemClicked = Signal(str)  # Signal émis quand l'élément est cliqué
    itemRemoved = Signal(str)  # Signal émis quand l'élément est supprimé

    def __init__(
        self,
        item_id: str,
        text: str,
        parent: Optional[QWidget] = None,
        icon: Optional[Union[str, Any]] = None,
        compact: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent)
        self.setProperty("type", "DraggableItem")

        # Initialisation des attributs
        self.item_id = item_id
        self.text = text
        self.is_dragging = False
        self.drag_start_pos = QPoint()
        self._compact = compact

        # Configuration du widget
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)
        self.setMidLineWidth(0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Hauteur selon le mode compact
        if self._compact:
            self.setMinimumHeight(24)
            self.setMaximumHeight(32)
        else:
            self.setMinimumHeight(40)
            self.setMaximumHeight(60)

        # Layout principal
        layout = QHBoxLayout(self)
        if self._compact:
            layout.setContentsMargins(6, 2, 6, 2)  # Marges réduites en mode compact
        else:
            layout.setContentsMargins(8, 4, 8, 4)  # Marges normales
        layout.setSpacing(8)

        # Icône par défaut pour le drag & drop si aucune icône n'est fournie
        if icon is None:
            icon = "https://img.icons8.com/?size=100&id=8329&format=png&color=000000"

        # Widget de contenu (HoverLabel avec icône de suppression)
        icon_size = QSize(16, 16) if self._compact else QSize(20, 20)
        icon_padding = 2 if self._compact else 4

        self.content_widget = HoverLabel(
            text=text,
            icon=icon,  # Icône poubelle pour la suppression
            icon_size=icon_size,
            icon_padding=icon_padding,
            **kwargs,
        )
        self.content_widget.hoverIconClicked.connect(self._on_remove_clicked)

        # Propriété pour la couleur de l'icône
        self._icon_color = "grey"
        # Appliquer la couleur initiale
        self.content_widget.icon_color = self._icon_color

        # Ajout du widget au layout (prend toute la largeur)
        layout.addWidget(self.content_widget)

    def _on_remove_clicked(self) -> None:
        """Gestionnaire de clic sur l'icône de suppression."""
        self.itemRemoved.emit(self.item_id)

    @property
    def icon_color(self) -> str:
        """Obtenir la couleur de l'icône du HoverLabel."""
        return self._icon_color

    @icon_color.setter
    def icon_color(self, value: str) -> None:
        """Définir la couleur de l'icône du HoverLabel."""
        self._icon_color = value
        if self.content_widget:
            self.content_widget.icon_color = value

    @property
    def compact(self) -> bool:
        """Obtenir le mode compact."""
        return self._compact

    @compact.setter
    def compact(self, value: bool) -> None:
        """Définir le mode compact et ajuster la hauteur."""
        self._compact = value
        if self._compact:
            self.setMinimumHeight(24)
            self.setMaximumHeight(32)
        else:
            self.setMinimumHeight(40)
            self.setMaximumHeight(60)
        self.updateGeometry()  # Forcer la mise à jour du layout

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Début du drag & drop."""
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Gestion du mouvement de souris pour le drag & drop."""
        if not (event.buttons() & Qt.LeftButton):
            return

        if not self.is_dragging:
            if (
                event.position().toPoint() - self.drag_start_pos
            ).manhattanLength() < 10:
                return

            self.is_dragging = True
            self.setProperty("dragging", True)
            self.style().unpolish(self)
            self.style().polish(self)

            # Créer le drag
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(self.item_id)
            drag.setMimeData(mime_data)

            # Exécuter le drag
            drag.exec(Qt.MoveAction)

            # Nettoyer après le drag
            self.is_dragging = False
            self.setProperty("dragging", False)
            self.style().unpolish(self)
            self.style().polish(self)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Fin du drag & drop."""
        self.is_dragging = False
        self.setProperty("dragging", False)
        self.style().unpolish(self)
        self.style().polish(self)
        super().mouseReleaseEvent(event)

    # OVERRIDE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def sizeHint(self) -> QSize:
        """Taille suggérée du widget basée sur le contenu."""
        # Obtenir la taille suggérée du HoverLabel
        content_size = self.content_widget.sizeHint()

        # Ajouter les marges et le padding du layout
        layout_margins = self.layout().contentsMargins()
        layout_spacing = self.layout().spacing()

        # Calculer la largeur totale
        total_width = (
            content_size.width() + layout_margins.left() + layout_margins.right()
        )

        # Calculer la hauteur totale selon le mode compact
        if self._compact:
            min_height = max(
                24,
                content_size.height() + layout_margins.top() + layout_margins.bottom(),
            )
            max_height = 32
        else:
            min_height = max(
                40,
                content_size.height() + layout_margins.top() + layout_margins.bottom(),
            )
            max_height = 60

        return QSize(total_width, min(min_height, max_height))

    def minimumSizeHint(self) -> QSize:
        """Taille minimale du widget."""
        # Obtenir la taille minimale du HoverLabel
        content_min_size = self.content_widget.minimumSizeHint()

        # Ajouter les marges du layout
        layout_margins = self.layout().contentsMargins()

        # Largeur minimale basée sur le contenu + marges
        min_width = (
            content_min_size.width() + layout_margins.left() + layout_margins.right()
        )

        # Hauteur minimale selon le mode compact
        min_height = 24 if self._compact else 40

        return QSize(min_width, min_height)

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refresh_style(self) -> None:
        """Refresh the widget's style (useful after dynamic stylesheet changes)."""
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


class DraggableList(QWidget):
    """
    Widget de liste d'éléments réorganisables avec drag & drop et suppression.

    Ce widget permet de gérer une liste d'éléments que l'utilisateur peut
    réorganiser par drag & drop et supprimer individuellement.

    Features:
        - Liste d'éléments réorganisables par drag & drop
        - Suppression d'éléments via HoverLabel (icône rouge au survol)
        - Interface cohérente avec HoverLabel pour tous les éléments
        - Signaux pour les événements de réorganisation et suppression
        - Interface fluide et intuitive
        - Personnalisation des apparences
        - Gestion automatique de l'ordre des éléments
        - Icône de suppression intégrée dans HoverLabel

    Example
    -------
    >>> draggable_list = DraggableList(
    ...     items=["Item 1", "Item 2", "Item 3"],
    ...     icon="https://img.icons8.com/?size=100&id=8329&format=png&color=000000"
    ... )
    >>> draggable_list.itemMoved.connect(lambda old_pos, new_pos: print(f"Moved from {old_pos} to {new_pos}"))
    >>> draggable_list.itemRemoved.connect(lambda item_id: print(f"Removed {item_id}"))

    Use cases
    ---------
    - Liste de tâches réorganisables
    - Sélecteur d'options avec ordre personnalisable
    - Interface de gestion de fichiers
    - Configuration d'éléments en ordre de priorité

    Parameters
    ----------
    parent : QWidget, optional
        Le widget parent (default: None).
    items : List[str], optional
        Liste initiale des éléments (default: []).
    allow_drag_drop : bool, optional
        Autoriser le drag & drop pour réorganiser (default: True).
    allow_remove : bool, optional
        Autoriser la suppression d'éléments via HoverLabel (default: True).
    max_height : int, optional
        Hauteur maximale du widget (default: 300).
    min_width : int, optional
        Largeur minimale du widget (default: 200).
    compact : bool, optional
        Afficher les éléments en mode compact (hauteur réduite) (default: False).
    *args, **kwargs :
        Arguments supplémentaires passés aux widgets d'éléments.

    Properties
    ----------
    items : List[str]
        Obtenir ou définir la liste des éléments.
    item_count : int
        Nombre d'éléments dans la liste (lecture seule).
    allow_drag_drop : bool
        Obtenir ou définir l'autorisation de drag & drop.
    allow_remove : bool
        Obtenir ou définir l'autorisation de suppression.
    icon_color : str
        Obtenir ou définir la couleur de l'icône des éléments.
    compact : bool
        Obtenir ou définir le mode compact.
    min_width : int
        Obtenir ou définir la largeur minimale du widget.

    Signals
    -------
    itemMoved(str, int, int)
        Émis quand un élément est déplacé (item_id, old_position, new_position).
    itemRemoved(str, int)
        Émis quand un élément est supprimé (item_id, position).
    itemAdded(str, int)
        Émis quand un élément est ajouté (item_id, position).
    itemClicked(str)
        Émis quand un élément est cliqué (item_id).
    orderChanged(List[str])
        Émis quand l'ordre des éléments change (nouvelle liste ordonnée).
    """

    itemMoved = Signal(str, int, int)  # item_id, old_position, new_position
    itemRemoved = Signal(str, int)  # item_id, position
    itemAdded = Signal(str, int)  # item_id, position
    itemClicked = Signal(str)  # item_id
    orderChanged = Signal(list)  # nouvelle liste ordonnée

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        items: Optional[List[str]] = None,
        allow_drag_drop: bool = True,
        allow_remove: bool = True,
        max_height: int = 300,
        min_width: int = 150,
        compact: bool = False,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent)
        self.setProperty("type", "DraggableList")

        # Initialisation des attributs
        self._items: List[str] = items or []
        self._allow_drag_drop: bool = allow_drag_drop
        self._allow_remove: bool = allow_remove
        self._max_height: int = max_height
        self._min_width: int = min_width
        self._compact: bool = compact
        self._item_widgets: Dict[str, DraggableItem] = {}  # item_id -> DraggableItem
        self._kwargs = kwargs
        self._icon_color = "grey"  # Couleur par défaut de l'icône

        # Configuration du widget
        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumWidth(min_width)
        self.setMaximumHeight(max_height)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Zone de scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setFrameStyle(QFrame.NoFrame)

        # Widget conteneur pour les éléments
        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout(self.container_widget)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(4)
        self.container_layout.addStretch()  # Espace flexible à la fin

        self.scroll_area.setWidget(self.container_widget)
        layout.addWidget(self.scroll_area)

        # Initialiser les éléments
        self._create_items()

    # PROPERTIES
    # ///////////////////////////////////////////////////////////////

    @property
    def items(self) -> List[str]:
        """Obtenir la liste des éléments."""
        return self._items.copy()

    @items.setter
    def items(self, value: List[str]) -> None:
        """Définir la liste des éléments."""
        self._items = value.copy()
        self._create_items()

    @property
    def item_count(self) -> int:
        """Nombre d'éléments dans la liste."""
        return len(self._items)

    @property
    def allow_drag_drop(self) -> bool:
        """Obtenir l'autorisation de drag & drop."""
        return self._allow_drag_drop

    @allow_drag_drop.setter
    def allow_drag_drop(self, value: bool) -> None:
        """Définir l'autorisation de drag & drop."""
        self._allow_drag_drop = value

    @property
    def allow_remove(self) -> bool:
        """Obtenir l'autorisation de suppression."""
        return self._allow_remove

    @allow_remove.setter
    def allow_remove(self, value: bool) -> None:
        """Définir l'autorisation de suppression."""
        self._allow_remove = value
        for widget in self._item_widgets.values():
            widget.content_widget.icon_enabled = value

    @property
    def icon_color(self) -> str:
        """Obtenir la couleur de l'icône des éléments."""
        return self._icon_color

    @icon_color.setter
    def icon_color(self, value: str) -> None:
        """Définir la couleur de l'icône de tous les éléments."""
        self._icon_color = value
        for widget in self._item_widgets.values():
            widget.icon_color = value

    @property
    def compact(self) -> bool:
        """Obtenir le mode compact."""
        return self._compact

    @compact.setter
    def compact(self, value: bool) -> None:
        """Définir le mode compact et mettre à jour tous les éléments."""
        self._compact = value
        for widget in self._item_widgets.values():
            widget.compact = value

    @property
    def min_width(self) -> int:
        """Obtenir la largeur minimale du widget."""
        return self._min_width

    @min_width.setter
    def min_width(self, value: int) -> None:
        """Définir la largeur minimale du widget."""
        self._min_width = value
        self.updateGeometry()  # Forcer la mise à jour du layout

    # ITEM MANAGEMENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def add_item(self, item_id: str, text: Optional[str] = None) -> None:
        """
        Ajouter un élément à la liste.

        Parameters
        ----------
        item_id : str
            Identifiant unique de l'élément.
        text : str, optional
            Texte à afficher (utilise item_id si None).
        """
        if item_id in self._items:
            return  # Élément déjà présent

        text = text or item_id
        self._items.append(item_id)

        # Créer le widget
        item_widget = DraggableItem(
            item_id=item_id, text=text, compact=self._compact, **self._kwargs
        )

        # Connecter les signaux
        item_widget.itemRemoved.connect(self._on_item_removed)

        # Masquer l'icône de suppression si nécessaire
        if not self._allow_remove:
            item_widget.content_widget.icon_enabled = False

        # Ajouter au layout (avant le stretch)
        self.container_layout.insertWidget(len(self._items) - 1, item_widget)
        self._item_widgets[item_id] = item_widget

        # Émettre le signal
        self.itemAdded.emit(item_id, len(self._items) - 1)
        self.orderChanged.emit(self._items.copy())

    def remove_item(self, item_id: str) -> bool:
        """
        Supprimer un élément de la liste.

        Parameters
        ----------
        item_id : str
            Identifiant de l'élément à supprimer.

        Returns
        -------
        bool
            True si l'élément a été supprimé, False sinon.
        """
        if item_id not in self._items:
            return False

        # Supprimer de la liste
        position = self._items.index(item_id)
        self._items.remove(item_id)

        # Supprimer le widget
        if item_id in self._item_widgets:
            widget = self._item_widgets[item_id]
            self.container_layout.removeWidget(widget)
            widget.deleteLater()
            del self._item_widgets[item_id]

        # Émettre les signaux
        self.itemRemoved.emit(item_id, position)
        self.orderChanged.emit(self._items.copy())

        return True

    def clear_items(self) -> None:
        """Supprimer tous les éléments de la liste."""
        # Nettoyer les widgets
        for widget in self._item_widgets.values():
            self.container_layout.removeWidget(widget)
            widget.deleteLater()
        self._item_widgets.clear()

        # Vider la liste
        self._items.clear()

        # Émettre le signal
        self.orderChanged.emit([])

    def move_item(self, item_id: str, new_position: int) -> bool:
        """
        Déplacer un élément à une nouvelle position.

        Parameters
        ----------
        item_id : str
            Identifiant de l'élément à déplacer.
        new_position : int
            Nouvelle position (0-based).

        Returns
        -------
        bool
            True si l'élément a été déplacé, False sinon.
        """
        if item_id not in self._items:
            return False

        old_position = self._items.index(item_id)
        if old_position == new_position:
            return True

        # Déplacer dans la liste
        self._items.pop(old_position)
        self._items.insert(new_position, item_id)

        # Déplacer le widget
        if item_id in self._item_widgets:
            widget = self._item_widgets[item_id]
            self.container_layout.removeWidget(widget)
            self.container_layout.insertWidget(new_position, widget)

        # Émettre les signaux
        self.itemMoved.emit(item_id, old_position, new_position)
        self.orderChanged.emit(self._items.copy())

        return True

    def get_item_position(self, item_id: str) -> int:
        """
        Obtenir la position d'un élément.

        Parameters
        ----------
        item_id : str
            Identifiant de l'élément.

        Returns
        -------
        int
            Position de l'élément (-1 si non trouvé).
        """
        try:
            return self._items.index(item_id)
        except ValueError:
            return -1

    def _create_items(self) -> None:
        """Créer les widgets pour tous les éléments."""
        # Nettoyer les widgets existants
        for widget in self._item_widgets.values():
            self.container_layout.removeWidget(widget)
            widget.deleteLater()
        self._item_widgets.clear()

        # Créer les nouveaux widgets
        for i, item_id in enumerate(self._items):
            item_widget = DraggableItem(
                item_id=item_id, text=item_id, compact=self._compact, **self._kwargs
            )

            # Connecter les signaux
            item_widget.itemRemoved.connect(self._on_item_removed)

            # Masquer l'icône de suppression si nécessaire
            if not self._allow_remove:
                item_widget.content_widget.icon_enabled = False

            # Ajouter au layout
            self.container_layout.insertWidget(i, item_widget)
            self._item_widgets[item_id] = item_widget

    def _on_item_removed(self, item_id: str) -> None:
        """Gestionnaire de suppression d'un élément."""
        self.remove_item(item_id)

    # EVENT FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Gestionnaire d'entrée de drag."""
        if self._allow_drag_drop and event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        """Gestionnaire de mouvement de drag."""
        if self._allow_drag_drop and event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        """Gestionnaire de drop."""
        if not self._allow_drag_drop:
            return

        item_id = event.mimeData().text()
        if item_id not in self._items:
            return

        # Calculer la nouvelle position
        drop_pos = event.position().toPoint()
        new_position = self._calculate_drop_position(drop_pos)

        # Déplacer l'élément
        self.move_item(item_id, new_position)

        event.acceptProposedAction()

    # UI FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def _calculate_drop_position(self, drop_pos: QPoint) -> int:
        """Calculer la position de drop basée sur les coordonnées."""
        # Convertir les coordonnées globales en coordonnées locales du container
        local_pos = self.container_widget.mapFrom(self, drop_pos)

        # Trouver la position dans le layout
        for i in range(self.container_layout.count() - 1):  # -1 pour exclure le stretch
            item = self.container_layout.itemAt(i)
            if item.widget():
                widget_rect = item.widget().geometry()
                if local_pos.y() < widget_rect.center().y():
                    return i

        return len(self._items) - 1

    # OVERRIDE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def sizeHint(self) -> QSize:
        """Taille suggérée du widget basée sur le contenu."""
        # Calculer la largeur maximale des éléments
        max_item_width = 0

        if self._item_widgets:
            # Obtenir la largeur maximale des éléments existants
            item_widths = [
                widget.sizeHint().width() for widget in self._item_widgets.values()
            ]
            max_item_width = max(item_widths) if item_widths else 0

        # Utiliser la largeur minimale seulement si nécessaire
        if max_item_width < self._min_width:
            max_item_width = self._min_width

        # Ajouter les marges du widget principal
        margins = self.contentsMargins()
        total_width = max_item_width + margins.left() + margins.right()

        # Calculer la hauteur basée sur le nombre d'éléments
        item_height = 50  # Hauteur approximative d'un élément
        spacing = 4  # Espacement entre éléments
        total_items_height = len(self._item_widgets) * (item_height + spacing)

        # Ajouter les marges et limiter à la hauteur maximale
        total_height = min(
            total_items_height + margins.top() + margins.bottom(), self._max_height
        )

        return QSize(total_width, max(200, total_height))

    def minimumSizeHint(self) -> QSize:
        """Taille minimale du widget."""
        # Largeur minimale basée sur les éléments ou la largeur minimale configurée
        min_width = 0

        if self._item_widgets:
            # Obtenir la largeur minimale des éléments existants
            item_min_widths = [
                widget.minimumSizeHint().width()
                for widget in self._item_widgets.values()
            ]
            min_width = max(item_min_widths) if item_min_widths else 0

        # Utiliser la largeur minimale seulement si nécessaire
        if min_width < self._min_width:
            min_width = self._min_width

        # Ajouter les marges
        margins = self.contentsMargins()
        total_width = min_width + margins.left() + margins.right()

        # Hauteur minimale basée sur au moins un élément
        item_min_height = 40  # Hauteur minimale d'un élément
        spacing = 4  # Espacement
        min_height = item_min_height + spacing + margins.top() + margins.bottom()

        return QSize(total_width, min_height)

    # STYLE FUNCTIONS
    # ///////////////////////////////////////////////////////////////

    def refresh_style(self) -> None:
        """Refresh the widget's style (useful after dynamic stylesheet changes)."""
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
