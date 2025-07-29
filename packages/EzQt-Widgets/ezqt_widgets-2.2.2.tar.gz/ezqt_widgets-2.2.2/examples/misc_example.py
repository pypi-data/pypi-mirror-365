#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

"""
Exemple d'utilisation des widgets misc EzQt_Widgets.

Ce script démontre l'utilisation de tous les types de widgets misc disponibles :
- OptionSelector
- CircularTimer
- ToggleIcon
- ToggleSwitch
- DraggableList
"""

import sys
import os
import re
import yaml
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QMessageBox,
    QScrollArea,
)

# Import des widgets EzQt
from ezqt_widgets.misc import (
    OptionSelector,
    CircularTimer,
    ToggleIcon,
    ToggleSwitch,
    DraggableList,
)


def load_and_apply_qss(app, qss_path, yaml_path, theme_name="dark"):
    """Fonction utilitaire pour charger et appliquer le QSS avec variables."""
    try:
        # Charger les variables du thème depuis le YAML
        with open(yaml_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        theme_vars = config["theme_palette"][theme_name]

        # Charger le QSS
        with open(qss_path, encoding="utf-8") as f:
            qss = f.read()

        # Remplacer les variables $ par leur valeur
        def repl(match):
            var = match.group(0)
            return theme_vars.get(var, var)

        qss = re.sub(r"\$_[a-zA-Z0-9_]+", repl, qss)
        app.setStyleSheet(qss)
        print(f"Thème '{theme_name}' chargé avec succès")

    except Exception as e:
        print(f"Erreur lors du chargement du thème: {e}")
        # Appliquer un style par défaut en cas d'erreur
        app.setStyleSheet("")


class MiscExampleWidget(QWidget):
    """Widget de démonstration pour tous les widgets misc."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Exemples Misc - EzQt_Widgets")
        self.setMinimumSize(900, 800)
        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface utilisateur."""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Création du ScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QScrollArea.NoFrame)

        # Widget conteneur pour le contenu
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Titre
        title = QLabel("Exemples Misc - EzQt_Widgets")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        content_layout.addWidget(title)

        # Groupe OptionSelector
        option_group = QGroupBox("OptionSelector")
        option_layout = QVBoxLayout(option_group)

        option_label = QLabel("Sélecteur d'options avec différentes configurations:")
        option_layout.addWidget(option_label)

        # Création d'un sélecteur d'options
        options = ["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"]
        self.option_selector = OptionSelector(options, default_id=0)
        self.option_selector.valueChanged.connect(self.on_option_changed)
        option_layout.addWidget(self.option_selector)

        self.option_output = QLabel("Option sélectionnée: Option 1")
        self.option_output.setStyleSheet("font-weight: bold; color: #4CAF50;")
        option_layout.addWidget(self.option_output)

        content_layout.addWidget(option_group)

        # Groupe CircularTimer
        timer_group = QGroupBox("CircularTimer")
        timer_layout = QVBoxLayout(timer_group)

        timer_label = QLabel("Timer circulaire avec contrôle:")
        timer_layout.addWidget(timer_label)

        # Layout horizontal pour le timer et les contrôles
        timer_control_layout = QHBoxLayout()

        self.circular_timer = CircularTimer(
            duration=10000
        )  # 10 secondes (en millisecondes)
        timer_control_layout.addWidget(self.circular_timer)

        # Contrôles pour le timer
        timer_buttons_layout = QVBoxLayout()

        start_button = QPushButton("Démarrer")
        start_button.clicked.connect(self.start_timer)
        timer_buttons_layout.addWidget(start_button)

        stop_button = QPushButton("Arrêter")
        stop_button.clicked.connect(self.stop_timer)
        timer_buttons_layout.addWidget(stop_button)

        reset_button = QPushButton("Réinitialiser")
        reset_button.clicked.connect(self.reset_timer)
        timer_buttons_layout.addWidget(reset_button)

        timer_control_layout.addLayout(timer_buttons_layout)
        timer_layout.addLayout(timer_control_layout)

        self.timer_status = QLabel("État: Arrêté")
        timer_layout.addWidget(self.timer_status)

        # Connexion des signaux du timer
        self.circular_timer.cycleCompleted.connect(self.on_timer_timeout)
        # Mise à jour manuelle du statut car CircularTimer n'a pas de signaux started/stopped

        content_layout.addWidget(timer_group)

        # Groupe ToggleIcon
        toggle_icon_group = QGroupBox("ToggleIcon")
        toggle_icon_layout = QVBoxLayout(toggle_icon_group)

        toggle_icon_label = QLabel("Icône basculante:")
        toggle_icon_layout.addWidget(toggle_icon_label)

        # Création d'icônes simples
        pixmap1 = QPixmap(32, 32)
        pixmap1.fill(Qt.green)
        icon1 = QIcon(pixmap1)

        pixmap2 = QPixmap(32, 32)
        pixmap2.fill(Qt.red)
        icon2 = QIcon(pixmap2)

        self.toggle_icon = ToggleIcon(opened_icon=icon1, closed_icon=icon2)
        self.toggle_icon.setToolTip("Cliquez pour basculer")
        self.toggle_icon.clicked.connect(self.on_toggle_icon_clicked)
        toggle_icon_layout.addWidget(self.toggle_icon)

        self.toggle_icon_status = QLabel("État: Icône 1")
        toggle_icon_layout.addWidget(self.toggle_icon_status)

        content_layout.addWidget(toggle_icon_group)

        # Groupe ToggleSwitch
        toggle_switch_group = QGroupBox("ToggleSwitch")
        toggle_switch_layout = QVBoxLayout(toggle_switch_group)

        toggle_switch_label = QLabel("Interrupteur basculant:")
        toggle_switch_layout.addWidget(toggle_switch_label)

        self.toggle_switch = ToggleSwitch(checked=False)
        self.toggle_switch.toggled.connect(self.on_toggle_switch_changed)
        toggle_switch_layout.addWidget(self.toggle_switch)

        self.toggle_switch_status = QLabel("État: Désactivé")
        toggle_switch_layout.addWidget(self.toggle_switch_status)

        content_layout.addWidget(toggle_switch_group)

        # Groupe DraggableList
        item_list_group = QGroupBox("DraggableList")
        item_list_layout = QVBoxLayout(item_list_group)

        item_list_label = QLabel("Liste d'éléments réorganisables avec drag & drop:")
        item_list_layout.addWidget(item_list_label)

        # Création de la liste d'éléments
        initial_items = [
            "Premier élément",
            "Deuxième élément", 
            "Troisième élément",
            "Quatrième élément",
        ]

        # Liste en mode normal
        self.item_list = DraggableList(
            items=initial_items,
            icon_color="#FF4444",
            max_height=200,
            min_width=120
        )
        self.item_list.itemRemoved.connect(self.on_item_removed)
        self.item_list.itemMoved.connect(self.on_item_moved)
        self.item_list.orderChanged.connect(self.on_order_changed)
        item_list_layout.addWidget(self.item_list)

        # Liste en mode compact
        compact_label = QLabel("Liste en mode compact:")
        item_list_layout.addWidget(compact_label)

        self.compact_list = DraggableList(
            items=["Option A", "Option B", "Option C"],
            compact=True,
            icon_color="grey",
            max_height=150
        )
        self.compact_list.itemRemoved.connect(self.on_item_removed)
        self.compact_list.itemMoved.connect(self.on_item_moved)
        item_list_layout.addWidget(self.compact_list)

        # Contrôles pour la liste
        item_controls_layout = QHBoxLayout()

        add_button = QPushButton("Ajouter")
        add_button.clicked.connect(self.add_item)
        item_controls_layout.addWidget(add_button)

        clear_button = QPushButton("Vider")
        clear_button.clicked.connect(self.item_list.clear_items)
        item_controls_layout.addWidget(clear_button)

        compact_toggle = QPushButton("Mode Compact")
        compact_toggle.setCheckable(True)
        compact_toggle.clicked.connect(self.toggle_compact_mode)
        item_controls_layout.addWidget(compact_toggle)

        item_list_layout.addLayout(item_controls_layout)

        self.item_list_status = QLabel("Éléments: 4 | Mode: Normal")
        item_list_layout.addWidget(self.item_list_status)

        content_layout.addWidget(item_list_group)

        # Boutons de test
        test_group = QGroupBox("Tests Interactifs")
        test_layout = QHBoxLayout(test_group)

        test_option_btn = QPushButton("Test Option")
        test_option_btn.clicked.connect(self.test_option_selector)
        test_layout.addWidget(test_option_btn)

        test_timer_btn = QPushButton("Test Timer")
        test_timer_btn.clicked.connect(self.test_circular_timer)
        test_layout.addWidget(test_timer_btn)

        test_toggle_btn = QPushButton("Test Toggle")
        test_toggle_btn.clicked.connect(self.test_toggle_widgets)
        test_layout.addWidget(test_toggle_btn)

        test_item_btn = QPushButton("Test Items")
        test_item_btn.clicked.connect(self.test_item_list)
        test_layout.addWidget(test_item_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_all)
        test_layout.addWidget(reset_btn)

        content_layout.addWidget(test_group)

        # Espacement en bas pour éviter que le contenu soit coupé
        content_layout.addStretch()

        # Configuration du ScrollArea
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Compteur pour les éléments
        self.item_counter = 5

    def on_option_changed(self, option):
        """Callback appelé quand une option est sélectionnée."""
        self.option_output.setText(f"Option sélectionnée: {option}")
        print(f"Option sélectionnée: {option}")

    def start_timer(self):
        """Démarre le timer."""
        self.circular_timer.startTimer()
        self.timer_status.setText("État: En cours")
        print("Timer démarré!")

    def stop_timer(self):
        """Arrête le timer."""
        self.circular_timer.stopTimer()
        self.timer_status.setText("État: Arrêté")
        print("Timer arrêté!")

    def reset_timer(self):
        """Réinitialise le timer."""
        self.circular_timer.resetTimer()
        self.timer_status.setText("État: Arrêté")
        print("Timer réinitialisé!")

    def on_timer_timeout(self):
        """Callback appelé quand le timer expire."""
        self.timer_status.setText("État: Terminé")
        print("Timer terminé!")

    def on_toggle_icon_clicked(self):
        """Callback appelé quand l'icône basculante est cliquée."""
        current_state = "Icône 2" if self.toggle_icon.state == "opened" else "Icône 1"
        self.toggle_icon_status.setText(f"État: {current_state}")
        print(f"Icône basculée vers: {current_state}")

    def on_toggle_switch_changed(self, checked):
        """Callback appelé quand l'interrupteur bascule."""
        state = "Activé" if checked else "Désactivé"
        self.toggle_switch_status.setText(f"État: {state}")
        print(f"Interrupteur: {state}")

    def on_item_removed(self, item_id, position):
        """Callback appelé quand un élément est supprimé."""
        print(f"Élément supprimé: {item_id} à la position {position}")
        self.update_item_count()

    def on_item_moved(self, item_id, old_pos, new_pos):
        """Callback appelé quand un élément est déplacé."""
        print(f"Élément déplacé: {item_id} de {old_pos} à {new_pos}")

    def on_order_changed(self, new_order):
        """Callback appelé quand l'ordre des éléments change."""
        print(f"Nouvel ordre: {new_order}")

    def add_item(self):
        """Ajoute un nouvel élément à la liste."""
        new_item = f"Élément {self.item_counter}"
        self.item_list.add_item(new_item, new_item)
        self.item_counter += 1
        self.update_item_count()
        print(f"Élément ajouté: {new_item}")

    def toggle_compact_mode(self):
        """Bascule entre le mode normal et compact."""
        is_compact = self.item_list.compact
        self.item_list.compact = not is_compact
        self.compact_list.compact = not is_compact
        
        mode = "Compact" if not is_compact else "Normal"
        self.update_item_count()
        print(f"Mode changé vers: {mode}")

    def update_item_count(self):
        """Met à jour le compteur d'éléments."""
        count = len(self.item_list.items)
        mode = "Compact" if self.item_list.compact else "Normal"
        self.item_list_status.setText(f"Éléments: {count} | Mode: {mode}")

    def test_option_selector(self):
        """Teste l'OptionSelector."""
        # Change vers l'option suivante
        current_id = self.option_selector.value_id
        next_id = (current_id + 1) % len(self.option_selector.options)
        self.option_selector.value_id = next_id
        print(f"Test: Option changée vers l'index {next_id}")

    def test_circular_timer(self):
        """Teste le CircularTimer."""
        if not self.circular_timer.running:
            self.start_timer()
        else:
            self.stop_timer()
        print("Test: Timer basculé")

    def test_toggle_widgets(self):
        """Teste les widgets de basculement."""
        # Bascule l'icône
        self.toggle_icon.click()
        # Bascule le switch
        self.toggle_switch.checked = not self.toggle_switch.checked
        print("Test: Widgets de basculement testés")

    def test_item_list(self):
        """Teste la DraggableList."""
        # Ajoute un élément de test
        self.add_item()
        # Bascule le mode compact
        self.toggle_compact_mode()
        print("Test: DraggableList testée (ajout + mode compact)")

    def reset_all(self):
        """Remet tout à zéro."""
        # Reset OptionSelector
        self.option_selector.value_id = 0
        self.option_output.setText("Option sélectionnée: Option 1")

        # Reset CircularTimer
        self.stop_timer()
        self.reset_timer()

        # Reset ToggleIcon
        self.toggle_icon_status.setText("État: Icône 1")

        # Reset ToggleSwitch
        self.toggle_switch.checked = False
        self.toggle_switch_status.setText("État: Désactivé")

        # Reset DraggableList
        initial_items = [
            "Premier élément",
            "Deuxième élément", 
            "Troisième élément",
            "Quatrième élément",
        ]
        self.item_list.items = initial_items
        self.item_list.compact = False
        self.compact_list.items = ["Option A", "Option B", "Option C"]
        self.compact_list.compact = True
        self.item_counter = 5
        self.update_item_count()

        print("Reset: Tous les widgets remis à zéro")


def main():
    """Fonction principale pour l'exécution individuelle."""
    app = QApplication(sys.argv)

    # Charger le thème depuis les fichiers
    bin_dir = os.path.join(os.path.dirname(__file__), "bin")
    qss_path = os.path.join(bin_dir, "main_theme.qss")
    yaml_path = os.path.join(bin_dir, "app.yaml")

    if os.path.exists(qss_path) and os.path.exists(yaml_path):
        load_and_apply_qss(app, qss_path, yaml_path, theme_name="dark")
    else:
        # Style par défaut si les fichiers de thème ne sont pas trouvés
        app.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 16px;
                text-align: center;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                color: #2c3e50;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """
        )

    window = MiscExampleWidget()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
