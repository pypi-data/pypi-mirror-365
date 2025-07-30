#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

"""
Exemple d'utilisation des widgets de label EzQt_Widgets.

Ce script démontre l'utilisation de tous les types de widgets de label disponibles :
- FramedLabel
- IndicatorLabel
- HoverLabel
- ClickableTagLabel
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
from ezqt_widgets.label import (
    FramedLabel,
    IndicatorLabel,
    HoverLabel,
    ClickableTagLabel,
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


class LabelExampleWidget(QWidget):
    """Widget de démonstration pour tous les types de labels."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Exemples de Labels - EzQt_Widgets")
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
        title = QLabel("Exemples de Labels - EzQt_Widgets")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        content_layout.addWidget(title)

        # Groupe FramedLabel
        framed_group = QGroupBox("FramedLabel")
        framed_layout = QVBoxLayout(framed_group)

        framed_label = QLabel("Labels avec cadre personnalisable:")
        framed_layout.addWidget(framed_label)

        # Layout horizontal pour les FramedLabel
        framed_buttons_layout = QHBoxLayout()

        self.framed_label1 = FramedLabel("Label 1")
        framed_buttons_layout.addWidget(self.framed_label1)

        self.framed_label2 = FramedLabel("Label 2")
        framed_buttons_layout.addWidget(self.framed_label2)

        self.framed_label3 = FramedLabel("Label 3")
        framed_buttons_layout.addWidget(self.framed_label3)

        framed_layout.addLayout(framed_buttons_layout)

        self.framed_output = QLabel("Label cliqué: Aucun")
        self.framed_output.setStyleSheet("font-weight: bold; color: #4CAF50;")
        framed_layout.addWidget(self.framed_output)

        content_layout.addWidget(framed_group)

        # Groupe IndicatorLabel
        indicator_group = QGroupBox("IndicatorLabel")
        indicator_layout = QVBoxLayout(indicator_group)

        indicator_label = QLabel("Indicateurs avec différents états:")
        indicator_layout.addWidget(indicator_label)

        # Création d'un status_map personnalisé pour nos indicateurs
        # Note: L'IndicatorLabel a des statuts par défaut: "neutral", "online", "partial", "offline"
        # Mais nous créons un status_map personnalisé pour avoir plus de contrôle
        custom_status_map = {
            "success": {"text": "Succès", "state": "ok", "color": "#4CAF50"},
            "error": {"text": "Erreur", "state": "ko", "color": "#F44336"},
            "warning": {
                "text": "Avertissement",
                "state": "partiel",
                "color": "#FFC107",
            },
            "info": {"text": "Information", "state": "none", "color": "#2196F3"},
        }

        # Boutons pour changer l'état des indicateurs
        button_layout = QHBoxLayout()

        self.success_indicator = IndicatorLabel(
            status_map=custom_status_map, initial_status="success"
        )
        button_layout.addWidget(self.success_indicator)

        self.error_indicator = IndicatorLabel(
            status_map=custom_status_map, initial_status="error"
        )
        button_layout.addWidget(self.error_indicator)

        self.warning_indicator = IndicatorLabel(
            status_map=custom_status_map, initial_status="warning"
        )
        button_layout.addWidget(self.warning_indicator)

        self.info_indicator = IndicatorLabel(
            status_map=custom_status_map, initial_status="info"
        )
        button_layout.addWidget(self.info_indicator)

        indicator_layout.addLayout(button_layout)

        # Bouton pour tester l'animation des indicateurs
        test_animation_btn = QPushButton("Test Animation")
        test_animation_btn.clicked.connect(self.test_indicator_animation)
        indicator_layout.addWidget(test_animation_btn)

        content_layout.addWidget(indicator_group)

        # Groupe HoverLabel
        hover_group = QGroupBox("HoverLabel")
        hover_layout = QVBoxLayout(hover_group)

        hover_label = QLabel("Labels avec effet de survol:")
        hover_layout.addWidget(hover_label)

        # Layout horizontal pour les HoverLabel
        hover_buttons_layout = QHBoxLayout()

        self.hover_label1 = HoverLabel("Survolez-moi pour voir l'effet!")
        self.hover_label1.hoverIconClicked.connect(self.on_hover_label_clicked)
        hover_buttons_layout.addWidget(self.hover_label1)

        self.hover_label2 = HoverLabel("Un autre label interactif")
        self.hover_label2.hoverIconClicked.connect(self.on_hover_label_clicked)
        hover_buttons_layout.addWidget(self.hover_label2)

        hover_layout.addLayout(hover_buttons_layout)

        self.hover_output = QLabel("Label survolé: Aucun")
        self.hover_output.setStyleSheet("font-weight: bold; color: #2196F3;")
        hover_layout.addWidget(self.hover_output)

        content_layout.addWidget(hover_group)

        # Groupe ClickableTagLabel
        tag_group = QGroupBox("ClickableTagLabel")
        tag_layout = QVBoxLayout(tag_group)

        tag_label = QLabel("Labels cliquables avec style de tag:")
        tag_layout.addWidget(tag_label)

        # Layout horizontal pour les ClickableTagLabel
        tag_buttons_layout = QHBoxLayout()

        self.tag_label1 = ClickableTagLabel("Tag 1")
        self.tag_label1.clicked.connect(self.on_tag_label_clicked)
        tag_buttons_layout.addWidget(self.tag_label1)

        self.tag_label2 = ClickableTagLabel("Tag 2")
        self.tag_label2.clicked.connect(self.on_tag_label_clicked)
        tag_buttons_layout.addWidget(self.tag_label2)

        self.tag_label3 = ClickableTagLabel("Tag 3")
        self.tag_label3.clicked.connect(self.on_tag_label_clicked)
        tag_buttons_layout.addWidget(self.tag_label3)

        tag_layout.addLayout(tag_buttons_layout)

        self.tag_output = QLabel("Tag cliqué: Aucun")
        self.tag_output.setStyleSheet("font-weight: bold; color: #FF9800;")
        tag_layout.addWidget(self.tag_output)

        content_layout.addWidget(tag_group)

        # Boutons de test
        test_group = QGroupBox("Tests Interactifs")
        test_layout = QHBoxLayout(test_group)

        test_framed_btn = QPushButton("Test Framed")
        test_framed_btn.clicked.connect(self.test_framed_labels)
        test_layout.addWidget(test_framed_btn)

        test_hover_btn = QPushButton("Test Hover")
        test_hover_btn.clicked.connect(self.test_hover_labels)
        test_layout.addWidget(test_hover_btn)

        test_tag_btn = QPushButton("Test Tags")
        test_tag_btn.clicked.connect(self.test_tag_labels)
        test_layout.addWidget(test_tag_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_all)
        test_layout.addWidget(reset_btn)

        content_layout.addWidget(test_group)

        # Espacement en bas pour éviter que le contenu soit coupé
        content_layout.addStretch()

        # Configuration du ScrollArea
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def on_framed_label_clicked(self):
        """Callback appelé quand un FramedLabel est cliqué."""
        sender = self.sender()
        if sender:
            text = sender.text()
            self.framed_output.setText(f"Label cliqué: {text}")
            print(f"FramedLabel cliqué: {text}")

    def on_hover_label_clicked(self):
        """Callback appelé quand un HoverLabel est cliqué."""
        sender = self.sender()
        if sender:
            text = sender.text()
            self.hover_output.setText(f"Label survolé: {text}")
            print(f"HoverLabel cliqué: {text}")

    def on_tag_label_clicked(self):
        """Callback appelé quand un ClickableTagLabel est cliqué."""
        sender = self.sender()
        if sender:
            text = sender.text()
            self.tag_output.setText(f"Tag cliqué: {text}")
            print(f"ClickableTagLabel cliqué: {text}")

    def test_indicator_animation(self):
        """Teste l'animation des indicateurs."""
        # Simule un changement d'état
        self.success_indicator.status = "error"
        self.error_indicator.status = "success"
        self.warning_indicator.status = "info"
        self.info_indicator.status = "warning"

        # Remet les états d'origine après 2 secondes
        QTimer.singleShot(2000, self.reset_indicators)

    def reset_indicators(self):
        """Remet les indicateurs dans leur état d'origine."""
        self.success_indicator.status = "success"
        self.error_indicator.status = "error"
        self.warning_indicator.status = "warning"
        self.info_indicator.status = "info"

    def test_framed_labels(self):
        """Teste les FramedLabel."""
        self.framed_label1.setText("Test 1")
        self.framed_label2.setText("Test 2")
        self.framed_label3.setText("Test 3")
        print("Test: Textes des FramedLabel modifiés")

    def test_hover_labels(self):
        """Teste les HoverLabel."""
        self.hover_label1.setText("Hover Test 1")
        self.hover_label2.setText("Hover Test 2")
        print("Test: Textes des HoverLabel modifiés")

    def test_tag_labels(self):
        """Teste les ClickableTagLabel."""
        self.tag_label1.setText("Tag Test 1")
        self.tag_label2.setText("Tag Test 2")
        self.tag_label3.setText("Tag Test 3")
        print("Test: Textes des ClickableTagLabel modifiés")

    def reset_all(self):
        """Remet tout à zéro."""
        # Reset FramedLabel
        self.framed_label1.setText("Label 1")
        self.framed_label2.setText("Label 2")
        self.framed_label3.setText("Label 3")
        self.framed_output.setText("Label cliqué: Aucun")

        # Reset HoverLabel
        self.hover_label1.setText("Survolez-moi pour voir l'effet!")
        self.hover_label2.setText("Un autre label interactif")
        self.hover_output.setText("Label survolé: Aucun")

        # Reset ClickableTagLabel
        self.tag_label1.setText("Tag 1")
        self.tag_label2.setText("Tag 2")
        self.tag_label3.setText("Tag 3")
        self.tag_output.setText("Tag cliqué: Aucun")

        # Reset IndicatorLabel
        self.reset_indicators()

        print("Reset: Tous les labels remis à zéro")


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

    window = LabelExampleWidget()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
