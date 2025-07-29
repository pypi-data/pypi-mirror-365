#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

"""
Exemple d'utilisation des widgets de boutons EzQt_Widgets.

Ce script démontre l'utilisation de tous les types de boutons disponibles :
- DateButton
- IconButton  
- LoaderButton
"""

import sys
import os
import re
import yaml
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
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
from ezqt_widgets.button import DateButton, IconButton, LoaderButton


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


class ButtonExampleWidget(QWidget):
    """Widget de démonstration pour tous les types de boutons."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Exemples de Boutons - EzQt_Widgets")
        self.setMinimumSize(800, 600)
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
        title = QLabel("Exemples de Boutons - EzQt_Widgets")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        content_layout.addWidget(title)

        # Groupe DateButton
        date_group = QGroupBox("DateButton")
        date_layout = QVBoxLayout(date_group)

        date_label = QLabel("Sélecteur de date avec validation:")
        date_layout.addWidget(date_label)

        self.date_button = DateButton()
        self.date_button.date = "2024-01-15"
        self.date_button.dateChanged.connect(self.on_date_changed)
        date_layout.addWidget(self.date_button)

        self.date_output = QLabel("Date sélectionnée: 2024-01-15")
        self.date_output.setStyleSheet("font-weight: bold; color: #4CAF50;")
        date_layout.addWidget(self.date_output)

        content_layout.addWidget(date_group)

        # Groupe IconButton
        icon_group = QGroupBox("IconButton")
        icon_layout = QVBoxLayout(icon_group)

        icon_label = QLabel("Bouton avec icône et texte:")
        icon_layout.addWidget(icon_label)

        # Création d'une icône simple pour l'exemple
        from PySide6.QtGui import QPixmap, QIcon

        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.blue)
        icon = QIcon(pixmap)

        self.icon_button = IconButton()
        self.icon_button.setIcon(icon)
        self.icon_button.setText("Bouton avec Icône")
        self.icon_button.clicked.connect(self.on_icon_button_clicked)
        icon_layout.addWidget(self.icon_button)

        self.icon_output = QLabel("Clics: 0")
        self.icon_output.setStyleSheet("font-weight: bold; color: #2196F3;")
        icon_layout.addWidget(self.icon_output)

        content_layout.addWidget(icon_group)

        # Groupe LoaderButton
        loader_group = QGroupBox("LoaderButton")
        loader_layout = QVBoxLayout(loader_group)

        loader_label = QLabel("Bouton de chargement avec états:")
        loader_layout.addWidget(loader_label)

        # Création du LoaderButton avec configuration complète
        self.loader_button = LoaderButton(
            text="Charger des données",
            loading_text="Chargement en cours...",
            auto_reset=True,
            success_display_time=2000,
            error_display_time=3000,
        )
        self.loader_button.clicked.connect(self.on_loader_button_clicked)
        loader_layout.addWidget(self.loader_button)

        self.loader_output = QLabel("État: Prêt")
        self.loader_output.setStyleSheet("font-weight: bold; color: #FF9800;")
        loader_layout.addWidget(self.loader_output)

        content_layout.addWidget(loader_group)

        # Boutons de test
        test_group = QGroupBox("Tests Interactifs")
        test_layout = QHBoxLayout(test_group)

        test_date_btn = QPushButton("Test Date")
        test_date_btn.clicked.connect(self.test_date_button)
        test_layout.addWidget(test_date_btn)

        test_loader_btn = QPushButton("Test Loader")
        test_loader_btn.clicked.connect(self.test_loader_button)
        test_layout.addWidget(test_loader_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_all)
        test_layout.addWidget(reset_btn)

        content_layout.addWidget(test_group)

        # Espacement en bas pour éviter que le contenu soit coupé
        content_layout.addStretch()

        # Configuration du ScrollArea
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Compteur de clics pour IconButton
        self.icon_click_count = 0

    def on_date_changed(self, date):
        """Callback appelé quand la date change."""
        self.date_output.setText(f"Date sélectionnée: {date}")
        print(f"Date changée: {date}")

    def on_icon_button_clicked(self):
        """Callback appelé quand le bouton icône est cliqué."""
        self.icon_click_count += 1
        self.icon_output.setText(f"Clics: {self.icon_click_count}")
        print(f"Bouton icône cliqué! Total: {self.icon_click_count}")

    def on_loader_button_clicked(self):
        """Callback appelé quand le bouton de chargement est cliqué."""
        self.loader_output.setText("État: Chargement...")
        print("Démarrage du chargement...")

        # Simuler un chargement
        QTimer.singleShot(2000, self.simulate_loading_complete)

    def simulate_loading_complete(self):
        """Simule la fin du chargement."""
        import random

        success = random.choice([True, False])

        if success:
            self.loader_output.setText("État: Succès!")
            print("Chargement réussi!")
        else:
            self.loader_output.setText("État: Erreur!")
            print("Erreur de chargement!")

    def test_date_button(self):
        """Teste le bouton de date."""
        from datetime import datetime, timedelta

        new_date = datetime.now() + timedelta(days=7)
        self.date_button.date = new_date.strftime("%Y-%m-%d")
        print(f"Test: Date changée vers {new_date.strftime('%Y-%m-%d')}")

    def test_loader_button(self):
        """Teste le bouton de chargement."""
        self.loader_button.click()
        print("Test: Démarrage du chargement")

    def reset_all(self):
        """Remet tout à zéro."""
        self.icon_click_count = 0
        self.icon_output.setText("Clics: 0")
        self.loader_output.setText("État: Prêt")
        self.date_button.date = "2024-01-15"
        print("Reset: Tous les compteurs remis à zéro")


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
        app.setStyleSheet("""
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
        """)

    window = ButtonExampleWidget()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
