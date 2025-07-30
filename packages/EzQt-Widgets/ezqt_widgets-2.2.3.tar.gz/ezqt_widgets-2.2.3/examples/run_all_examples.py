#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

"""
Script principal pour lancer tous les exemples de widgets EzQt_Widgets.

Ce script permet de choisir et lancer n'importe quel exemple de widget
disponible dans le dossier examples.
"""

import sys
import os
import re
import yaml
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QMessageBox,
    QStackedWidget,
    QFrame,
)

# Import des widgets d'exemple
from button_example import ButtonExampleWidget
from input_example import InputExampleWidget
from label_example import LabelExampleWidget
from misc_example import MiscExampleWidget


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


class EzQtExamplesLauncher(QMainWindow):
    """Launcher principal pour tous les exemples EzQt_Widgets."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("EzQt_Widgets - Launcher d'Exemples")
        self.setMinimumSize(1200, 800)
        self.setup_ui()
        self.setup_theme()

    def setup_ui(self):
        """Configure l'interface utilisateur."""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header avec titre et navigation
        self.setup_header(main_layout)

        # Zone de contenu avec stacked widget
        self.setup_content_area(main_layout)

        # Footer avec informations
        self.setup_footer(main_layout)

    def setup_header(self, main_layout):
        """Configure l'en-tête avec navigation."""
        # Header container
        header_frame = QFrame()
        header_frame.setObjectName("header")
        header_frame.setFixedHeight(120)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 20, 15)

        # Titre principal
        title = QLabel("EzQt_Widgets - Démonstration Complète")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("main-title")
        header_layout.addWidget(title)

        # Sous-titre
        subtitle = QLabel("Sélectionnez une catégorie pour explorer les widgets")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setObjectName("subtitle")
        header_layout.addWidget(subtitle)

        # Barre de navigation
        nav_frame = QFrame()
        nav_frame.setObjectName("nav-bar")
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setSpacing(10)
        nav_layout.setContentsMargins(0, 10, 0, 0)

        # Boutons de navigation
        self.nav_buttons = {}
        nav_items = [
            ("buttons", "Boutons", "🎯"),
            ("inputs", "Inputs", "⌨️"),
            ("labels", "Labels", "🏷️"),
            ("misc", "Misc", "🔧"),
        ]

        # Créer les widgets d'exemple d'abord pour savoir lesquels sont disponibles
        self.example_widgets = {}

        try:
            self.example_widgets["buttons"] = ButtonExampleWidget()
        except Exception as e:
            print(f"Erreur lors du chargement de ButtonExampleWidget: {e}")

        try:
            self.example_widgets["inputs"] = InputExampleWidget()
        except Exception as e:
            print(f"Erreur lors du chargement de InputExampleWidget: {e}")

        try:
            self.example_widgets["labels"] = LabelExampleWidget()
        except Exception as e:
            print(f"Erreur lors du chargement de LabelExampleWidget: {e}")

        try:
            self.example_widgets["misc"] = MiscExampleWidget()
        except Exception as e:
            print(f"Erreur lors du chargement de MiscExampleWidget: {e}")

        # Créer les boutons de navigation seulement pour les widgets disponibles
        for key, text, icon in nav_items:
            if key in self.example_widgets and self.example_widgets[key] is not None:
                btn = QPushButton(f"{icon} {text}")
                btn.setObjectName("nav-button")
                btn.setCheckable(True)
                btn.clicked.connect(lambda checked, k=key: self.switch_to_example(k))
                nav_layout.addWidget(btn)
                self.nav_buttons[key] = btn

        # Bouton actif par défaut (premier disponible)
        if self.nav_buttons:
            first_key = list(self.nav_buttons.keys())[0]
            self.nav_buttons[first_key].setChecked(True)

        header_layout.addWidget(nav_frame)
        main_layout.addWidget(header_frame)

    def setup_content_area(self, main_layout):
        """Configure la zone de contenu."""
        # Container pour le contenu
        content_frame = QFrame()
        content_frame.setObjectName("content-area")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Stacked widget pour les exemples
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("stacked-content")

        # Ajout des widgets au stacked widget
        for key, widget in self.example_widgets.items():
            if widget is not None:
                self.stacked_widget.addWidget(widget)

        content_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(content_frame)

    def setup_footer(self, main_layout):
        """Configure le pied de page."""
        # Footer container
        footer_frame = QFrame()
        footer_frame.setObjectName("footer")
        footer_frame.setFixedHeight(60)
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(20, 10, 20, 10)

        # Informations de version
        version_info = QLabel(
            "EzQt_Widgets v1.0.0 - Bibliothèque de widgets Qt personnalisés"
        )
        version_info.setObjectName("footer-text")
        footer_layout.addWidget(version_info)

        # Boutons d'action
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)

        help_btn = QPushButton("Aide")
        help_btn.setObjectName("footer-button")
        help_btn.clicked.connect(self.show_help)
        action_layout.addWidget(help_btn)

        about_btn = QPushButton("À propos")
        about_btn.setObjectName("footer-button")
        about_btn.clicked.connect(self.show_about)
        action_layout.addWidget(about_btn)

        footer_layout.addLayout(action_layout)
        main_layout.addWidget(footer_frame)

    def setup_theme(self):
        """Configure le thème global de l'application."""
        # Chemin vers les fichiers de thème
        bin_dir = os.path.join(os.path.dirname(__file__), "bin")
        qss_path = os.path.join(bin_dir, "main_theme.qss")
        yaml_path = os.path.join(bin_dir, "app.yaml")

        # Charger le thème depuis les fichiers
        if os.path.exists(qss_path) and os.path.exists(yaml_path):
            load_and_apply_qss(self, qss_path, yaml_path, theme_name="dark")
        else:
            # Style par défaut si les fichiers de thème ne sont pas trouvés
            self.setStyleSheet(
                """
                QMainWindow {
                    background-color: #f8f9fa;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #e9ecef;
                    border-radius: 8px;
                    margin-top: 1ex;
                    padding-top: 15px;
                    background-color: #f8f9fa;
                }
                QPushButton {
                    background-color: #3498db;
                    border: none;
                    color: white;
                    padding: 10px 20px;
                    text-align: center;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 6px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QLabel {
                    color: #2c3e50;
                    font-size: 13px;
                }
            """
            )

    def switch_to_example(self, example_key):
        """Change vers l'exemple sélectionné."""
        # Mise à jour des boutons de navigation
        for key, btn in self.nav_buttons.items():
            btn.setChecked(key == example_key)

        # Changement du widget affiché
        if example_key in self.example_widgets:
            self.stacked_widget.setCurrentWidget(self.example_widgets[example_key])
            print(f"Changement vers l'exemple: {example_key}")

    def show_help(self):
        """Affiche l'aide."""
        help_text = """
        <h3>Guide d'utilisation - EzQt_Widgets</h3>
        
        <p><b>Navigation :</b></p>
        <ul>
            <li>Utilisez les boutons de navigation en haut pour changer d'exemple</li>
            <li>Chaque exemple démontre une catégorie de widgets</li>
            <li>Interagissez avec les widgets pour voir leurs fonctionnalités</li>
        </ul>
        
        <p><b>Catégories disponibles :</b></p>
        <ul>
            <li><b>Boutons :</b> DateButton, IconButton, LoaderButton</li>
            <li><b>Inputs :</b> TabReplaceTextEdit, AutoCompleteInput, SearchInput, PasswordInput</li>
            <li><b>Labels :</b> FramedLabel, IndicatorLabel, HoverLabel, ClickableTagLabel</li>
            <li><b>Misc :</b> OptionSelector, CircularTimer, ToggleIcon, ToggleSwitch, DraggableList</li>
        </ul>
        
        <p><b>Tests :</b></p>
        <ul>
            <li>Utilisez les boutons "Test" pour voir les interactions</li>
            <li>Les boutons "Reset" remettent tout à zéro</li>
        </ul>
        """

        QMessageBox.information(self, "Aide - EzQt_Widgets", help_text)

    def show_about(self):
        """Affiche les informations à propos."""
        about_text = """
        <h3>EzQt_Widgets v1.0.0</h3>
        
        <p>Bibliothèque de widgets Qt personnalisés pour PySide6.</p>
        
        <p><b>Fonctionnalités :</b></p>
        <ul>
            <li>Widgets de boutons avancés</li>
            <li>Champs de saisie spécialisés</li>
            <li>Labels interactifs</li>
            <li>Widgets utilitaires divers</li>
        </ul>
        
        <p><b>Compatibilité :</b> PySide6</p>
        <p><b>Licence :</b> MIT</p>
        
        <p>Développé pour simplifier la création d'interfaces Qt modernes.</p>
        """

        QMessageBox.about(self, "À propos - EzQt_Widgets", about_text)

    def closeEvent(self, event):
        """Gestion de la fermeture de l'application."""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Voulez-vous vraiment quitter la démonstration ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    """Fonction principale."""
    app = QApplication(sys.argv)

    # Configuration de l'application
    app.setApplicationName("EzQt_Widgets Examples")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("EzQt_Widgets")

    # Création et affichage de la fenêtre principale
    window = EzQtExamplesLauncher()
    window.show()

    # Exécution de l'application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
