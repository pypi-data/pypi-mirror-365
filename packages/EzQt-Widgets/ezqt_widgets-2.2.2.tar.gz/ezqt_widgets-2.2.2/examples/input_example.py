#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

"""
Exemple d'utilisation des widgets d'entrée EzQt_Widgets.

Ce script démontre l'utilisation de tous les types de widgets d'entrée disponibles :
- TabReplaceTextEdit
- AutoCompleteInput
- SearchInput
- PasswordInput
"""

import sys
import os
import re
import yaml
from PySide6.QtCore import Qt
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
from ezqt_widgets.input import (
    TabReplaceTextEdit,
    AutoCompleteInput,
    SearchInput,
    PasswordInput,
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


class InputExampleWidget(QWidget):
    """Widget de démonstration pour tous les types d'inputs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Exemples d'Inputs - EzQt_Widgets")
        self.setMinimumSize(800, 700)
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
        title = QLabel("Exemples d'Inputs - EzQt_Widgets")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        content_layout.addWidget(title)

        # Groupe TabReplaceTextEdit
        tab_replace_group = QGroupBox("TabReplaceTextEdit")
        tab_replace_layout = QVBoxLayout(tab_replace_group)

        tab_replace_label = QLabel("Éditeur de texte avec remplacement de tabulation:")
        tab_replace_layout.addWidget(tab_replace_label)

        self.tab_replace_textedit = TabReplaceTextEdit()
        self.tab_replace_textedit.setPlaceholderText(
            "Tapez ici... Les tabulations seront remplacées par des espaces."
        )
        self.tab_replace_textedit.setMaximumHeight(100)
        self.tab_replace_textedit.textChanged.connect(self.on_tab_replace_changed)
        tab_replace_layout.addWidget(self.tab_replace_textedit)

        self.tab_replace_output = QLabel("Caractères: 0")
        self.tab_replace_output.setStyleSheet("font-weight: bold; color: #4CAF50;")
        tab_replace_layout.addWidget(self.tab_replace_output)

        content_layout.addWidget(tab_replace_group)

        # Groupe AutoCompleteInput
        autocomplete_group = QGroupBox("AutoCompleteInput")
        autocomplete_layout = QVBoxLayout(autocomplete_group)

        autocomplete_label = QLabel("Champ de saisie avec autocomplétion:")
        autocomplete_layout.addWidget(autocomplete_label)

        # Suggestions pour l'autocomplétion
        suggestions = [
            "Python",
            "JavaScript",
            "Java",
            "C++",
            "C#",
            "PHP",
            "Ruby",
            "Go",
            "Rust",
            "Swift",
        ]

        self.autocomplete_input = AutoCompleteInput()
        self.autocomplete_input.setPlaceholderText(
            "Tapez 'Py' ou 'Ja' pour voir les suggestions..."
        )
        self.autocomplete_input.suggestions = suggestions
        self.autocomplete_input.textChanged.connect(self.on_autocomplete_changed)
        autocomplete_layout.addWidget(self.autocomplete_input)

        self.autocomplete_output = QLabel("Texte saisi: ")
        self.autocomplete_output.setStyleSheet("font-weight: bold; color: #2196F3;")
        autocomplete_layout.addWidget(self.autocomplete_output)

        content_layout.addWidget(autocomplete_group)

        # Groupe SearchInput
        search_group = QGroupBox("SearchInput")
        search_layout = QVBoxLayout(search_group)

        search_label = QLabel("Champ de recherche avec validation:")
        search_layout.addWidget(search_label)

        self.search_input = SearchInput()
        self.search_input.setPlaceholderText(
            "Tapez pour rechercher et appuyez sur Entrée..."
        )
        self.search_input.searchSubmitted.connect(self.on_search_triggered)
        search_layout.addWidget(self.search_input)

        self.search_output = QLabel("Recherche: Aucune")
        self.search_output.setStyleSheet("font-weight: bold; color: #FF9800;")
        search_layout.addWidget(self.search_output)

        content_layout.addWidget(search_group)

        # Groupe PasswordInput
        password_group = QGroupBox("PasswordInput")
        password_layout = QVBoxLayout(password_group)

        password_label = QLabel("Champ de mot de passe avec indicateur de force:")
        password_layout.addWidget(password_label)

        # Création du PasswordInput avec configuration
        self.password_input = PasswordInput(show_strength=True, strength_bar_height=4)
        # Définir le placeholder via le widget interne
        self.password_input._password_input.setPlaceholderText(
            "Entrez votre mot de passe..."
        )
        # Connecter le signal de changement de texte
        self.password_input._password_input.textChanged.connect(
            self.on_password_changed
        )
        password_layout.addWidget(self.password_input)

        self.password_output = QLabel("Force du mot de passe: ")
        self.password_output.setStyleSheet("font-weight: bold; color: #E91E63;")
        password_layout.addWidget(self.password_output)

        content_layout.addWidget(password_group)

        # Boutons de test
        test_group = QGroupBox("Tests Interactifs")
        test_layout = QHBoxLayout(test_group)

        test_tab_btn = QPushButton("Test Tab")
        test_tab_btn.clicked.connect(self.test_tab_replace)
        test_layout.addWidget(test_tab_btn)

        test_search_btn = QPushButton("Test Search")
        test_search_btn.clicked.connect(self.test_search)
        test_layout.addWidget(test_search_btn)

        test_password_btn = QPushButton("Test Password")
        test_password_btn.clicked.connect(self.test_password)
        test_layout.addWidget(test_password_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_all)
        test_layout.addWidget(reset_btn)

        content_layout.addWidget(test_group)

        # Espacement en bas pour éviter que le contenu soit coupé
        content_layout.addStretch()

        # Configuration du ScrollArea
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def on_tab_replace_changed(self):
        """Callback appelé quand le texte change dans TabReplaceTextEdit."""
        text = self.tab_replace_textedit.toPlainText()
        char_count = len(text)
        self.tab_replace_output.setText(f"Caractères: {char_count}")
        print(f"Texte modifié: {char_count} caractères")

    def on_autocomplete_changed(self, text):
        """Callback appelé quand le texte change dans AutoCompleteInput."""
        self.autocomplete_output.setText(f"Texte saisi: {text}")
        print(f"Autocomplétion: {text}")

    def on_search_triggered(self, search_text):
        """Callback appelé quand une recherche est soumise."""
        self.search_output.setText(f"Recherche: '{search_text}'")
        print(f"Recherche soumise: {search_text}")

    def on_password_changed(self, password):
        """Callback appelé quand le mot de passe change."""
        strength = self.get_password_strength(password)
        self.password_output.setText(f"Force du mot de passe: {strength}")
        print(f"Mot de passe: {len(password)} caractères - Force: {strength}")

    def get_password_strength(self, password):
        """Évalue la force du mot de passe."""
        if not password:
            return "Aucun"

        score = 0
        if len(password) >= 8:
            score += 1
        if any(c.isupper() for c in password):
            score += 1
        if any(c.islower() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1

        if score <= 1:
            return "Faible"
        elif score <= 3:
            return "Moyenne"
        else:
            return "Forte"

    def test_tab_replace(self):
        """Teste le TabReplaceTextEdit."""
        test_text = (
            "Ligne 1\n\tLigne 2 avec tabulation\n\t\tLigne 3 avec double tabulation"
        )
        self.tab_replace_textedit.setPlainText(test_text)
        print("Test: Texte avec tabulations ajouté")

    def test_search(self):
        """Teste le SearchInput."""
        self.search_input.setText("test recherche")
        self.search_input.searchSubmitted.emit("test recherche")
        print("Test: Recherche simulée")

    def test_password(self):
        """Teste le PasswordInput."""
        test_password = "MotDePasse123!"
        self.password_input._password_input.setText(test_password)
        print("Test: Mot de passe de test ajouté")

    def reset_all(self):
        """Remet tout à zéro."""
        self.tab_replace_textedit.clear()
        self.autocomplete_input.clear()
        self.search_input.clear()
        self.password_input._password_input.clear()
        self.tab_replace_output.setText("Caractères: 0")
        self.autocomplete_output.setText("Texte saisi: ")
        self.search_output.setText("Recherche: Aucune")
        self.password_output.setText("Force du mot de passe: ")
        print("Reset: Tous les champs vidés")


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
            QLineEdit, QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #3498db;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """
        )

    window = InputExampleWidget()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
