# Documentation des Widgets de Labels

## Vue d'ensemble

Ce module contient des widgets de labels spécialisés qui étendent les fonctionnalités des widgets Qt standard. Ces widgets offrent des fonctionnalités avancées pour l'affichage de texte, les interactions utilisateur et les indicateurs visuels.

## Widgets Disponibles

### ClickableTagLabel

**Fichier :** `ezqt_widgets/label/clickable_tag_label.py`

**Description :** Label cliquable de type tag avec état basculable.

**Fonctionnalités :**
- Tag cliquable avec état activé/désactivé
- Émet des signaux lors du clic et du changement d'état
- Texte, police, largeur/hauteur minimale personnalisables
- Couleur de statut personnalisable (nom traditionnel ou hex)
- Compatible QSS (propriétés type/class/status)
- Calcul automatique de la taille minimale
- Focus clavier et accessibilité

**Paramètres :**
- `name` : str, optionnel - Texte à afficher dans le tag (défaut : "")
- `enabled` : bool, optionnel - État initial (défaut : False)
- `status_color` : str, optionnel - Couleur quand sélectionné (défaut : "#0078d4")
- `min_width` : int, optionnel - Largeur minimale (défaut : None, calculé automatiquement)
- `min_height` : int, optionnel - Hauteur minimale (défaut : None, calculé automatiquement)
- `parent` : QWidget, optionnel - Widget parent (défaut : None)

**Propriétés :**
- `name` : str - Obtenir ou définir le texte du tag
- `enabled` : bool - Obtenir ou définir l'état activé
- `status_color` : str - Obtenir ou définir la couleur de statut
- `min_width` : int - Obtenir ou définir la largeur minimale
- `min_height` : int - Obtenir ou définir la hauteur minimale

**Signaux :**
- `clicked()` - Émis quand le tag est cliqué
- `toggle_keyword(str)` - Émis avec le nom du tag lors du basculement
- `stateChanged(bool)` - Émis quand l'état activé change

**Exemple d'utilisation :**
```python
from ezqt_widgets.label import ClickableTagLabel

# Création d'un tag cliquable
tag = ClickableTagLabel(
    name="Python",
    enabled=False,
    status_color="#28a745"
)

# Connexion des signaux
tag.clicked.connect(lambda: print("Tag cliqué"))
tag.toggle_keyword.connect(lambda keyword: print(f"Tag basculé: {keyword}"))
tag.stateChanged.connect(lambda enabled: print(f"État changé: {enabled}"))

# Basculement de l'état
tag.enabled = True
```

---

### FramedLabel

**Fichier :** `ezqt_widgets/label/framed_label.py`

**Description :** Label flexible basé sur QFrame, conçu pour le style et la mise en page avancés dans les applications Qt.

**Fonctionnalités :**
- Accès basé sur les propriétés au texte du label (text) et à l'alignement (alignment)
- Émet un signal textChanged(str) quand le texte change
- Permet l'injection de feuille de style personnalisée pour l'apparence avancée
- Adapté pour une utilisation comme en-tête, label de section, ou tout contexte où un label stylé est nécessaire

**Paramètres :**
- `text` : str, optionnel - Le texte initial à afficher dans le label (défaut : "")
- `parent` : QWidget, optionnel - Widget parent (défaut : None)
- `alignment` : Qt.AlignmentFlag, optionnel - L'alignement du texte du label (défaut : Qt.AlignmentFlag.AlignCenter)
- `style_sheet` : str, optionnel - Feuille de style personnalisée à appliquer au QFrame (défaut : None, utilise un arrière-plan transparent)
- `min_width` : int, optionnel - Contrainte de largeur minimale pour le widget (défaut : None)
- `min_height` : int, optionnel - Contrainte de hauteur minimale pour le widget (défaut : None)

**Propriétés :**
- `text` : str - Obtenir ou définir le texte du label
- `alignment` : Qt.AlignmentFlag - Obtenir ou définir l'alignement du label
- `min_width` : int - Obtenir ou définir la contrainte de largeur minimale
- `min_height` : int - Obtenir ou définir la contrainte de hauteur minimale

**Signaux :**
- `textChanged(str)` - Émis quand le texte du label change

**Exemple d'utilisation :**
```python
from ezqt_widgets.label import FramedLabel
from PySide6.QtCore import Qt

# Création d'un label encadré
framed_label = FramedLabel(
    text="Titre de Section",
    alignment=Qt.AlignCenter,
    style_sheet="""
        QFrame {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 2px solid #0078d4;
            border-radius: 8px;
            padding: 8px;
        }
    """
)

# Connexion du signal
framed_label.textChanged.connect(lambda text: print(f"Texte changé: {text}"))

# Modification du texte
framed_label.text = "Nouveau Titre"
```

---

### HoverLabel

**Fichier :** `ezqt_widgets/label/hover_label.py`

**Description :** QLabel interactif qui affiche une icône flottante au survol et émet un signal quand l'icône est cliquée.

**Fonctionnalités :**
- Affiche une icône personnalisée au survol, avec opacité, taille, superposition de couleur et remplissage configurables
- Émet un signal hoverIconClicked quand l'icône est cliquée
- Gère les événements de souris et les changements de curseur pour une meilleure UX
- Le texte et l'icône peuvent être définis à la construction ou via les propriétés
- L'icône peut être activée/désactivée dynamiquement
- Supporte les icônes PNG/JPG et SVG (local, ressource, URL)
- Gestion robuste des erreurs de chargement d'icônes

**Paramètres :**
- `parent` : QWidget, optionnel - Widget parent (défaut : None)
- `icon` : QIcon ou str, optionnel - L'icône à afficher au survol (QIcon, chemin, ressource, URL, ou SVG)
- `text` : str, optionnel - Le texte du label (défaut : "")
- `opacity` : float, optionnel - L'opacité de l'icône de survol (défaut : 0.5)
- `icon_size` : QSize ou tuple, optionnel - La taille de l'icône de survol (défaut : QSize(16, 16))
- `icon_color` : QColor ou str, optionnel - Superposition de couleur optionnelle à appliquer à l'icône (défaut : None)
- `icon_padding` : int, optionnel - Remplissage (en px) à droite du texte pour l'icône (défaut : 8)
- `icon_enabled` : bool, optionnel - Si l'icône est affichée au survol (défaut : True)
- `min_width` : int, optionnel - Largeur minimale du widget (défaut : None)

**Propriétés :**
- `opacity` : float - Obtenir ou définir l'opacité de l'icône de survol
- `hover_icon` : QIcon - Obtenir ou définir l'icône affichée au survol
- `icon_size` : QSize - Obtenir ou définir la taille de l'icône de survol
- `icon_color` : QColor ou str ou None - Obtenir ou définir la superposition de couleur de l'icône de survol
- `icon_padding` : int - Obtenir ou définir le remplissage droit pour l'icône
- `icon_enabled` : bool - Activer ou désactiver l'icône de survol

**Signaux :**
- `hoverIconClicked()` - Émis quand l'icône de survol est cliquée

**Méthodes utilitaires :**
- `clear_icon()` - Efface l'icône

**Exemple d'utilisation :**
```python
from ezqt_widgets.label import HoverLabel
from PySide6.QtCore import QSize

# Création d'un label avec icône au survol
hover_label = HoverLabel(
    text="Survolez-moi pour voir l'icône",
    icon="icons/info.png",
    opacity=0.7,
    icon_size=QSize(20, 20),
    icon_color="#0078d4",
    icon_padding=10
)

# Connexion du signal
hover_label.hoverIconClicked.connect(lambda: print("Icône de survol cliquée"))

# Désactivation de l'icône
hover_label.icon_enabled = False

# Modification de l'icône
hover_label.hover_icon = "icons/help.png"
```

---

### IndicatorLabel

**Fichier :** `ezqt_widgets/label/indicator_label.py`

**Description :** Widget d'indicateur de statut dynamique basé sur QFrame, conçu pour afficher un label de statut et une LED colorée dans les applications Qt.

**Fonctionnalités :**
- États dynamiques définis via un dictionnaire configurable (status_map) (texte, état, couleur)
- Accès basé sur les propriétés au statut actuel (status)
- Émet un signal statusChanged(str) quand le statut change
- Permet des ensembles de statuts et couleurs personnalisés pour divers cas d'usage
- Adapté pour les indicateurs en ligne/hors ligne, statut de service, etc.

**Paramètres :**
- `parent` : QWidget, optionnel - Widget parent (défaut : None)
- `status_map` : dict, optionnel - Dictionnaire définissant les états possibles. Chaque clé est un nom d'état, et chaque valeur est un dict avec les clés :
  - text (str) : Le label à afficher
  - state (str) : La valeur définie comme propriété Qt pour le style
  - color (str) : La couleur de la LED (toute couleur CSS valide)
- `initial_status` : str, optionnel - La clé de statut initiale à utiliser (défaut : "neutral")

**Propriétés :**
- `status` : str - Obtenir ou définir la clé de statut actuelle

**Signaux :**
- `statusChanged(str)` - Émis quand le statut change

**Méthodes utilitaires :**
- `set_status(status)` - Définit le statut

**Exemple d'utilisation :**
```python
from ezqt_widgets.label import IndicatorLabel

# Définition des statuts personnalisés
status_map = {
    "offline": {
        "text": "Hors ligne",
        "state": "offline",
        "color": "#dc3545"
    },
    "online": {
        "text": "En ligne",
        "state": "online",
        "color": "#28a745"
    },
    "connecting": {
        "text": "Connexion...",
        "state": "connecting",
        "color": "#ffc107"
    },
    "error": {
        "text": "Erreur",
        "state": "error",
        "color": "#dc3545"
    }
}

# Création de l'indicateur
indicator = IndicatorLabel(
    status_map=status_map,
    initial_status="offline"
)

# Connexion du signal
indicator.statusChanged.connect(lambda status: print(f"Statut changé: {status}"))

# Changement de statut
indicator.status = "online"
indicator.set_status("connecting")
```

## Fonctions Utilitaires

### colorize_pixmap(pixmap, color, opacity)

Recolore un QPixmap avec la couleur et l'opacité données.

**Paramètres :**
- `pixmap` : QPixmap - Le pixmap à colorer
- `color` : str - La couleur à appliquer
- `opacity` : float - L'opacité (défaut : 0.5)

**Retourne :**
- `QPixmap` - Le pixmap coloré

### load_icon_from_source(source)

Charge une icône depuis diverses sources (QIcon, chemin, URL, etc.).

**Paramètres :**
- `source` : QIcon ou str ou None - Source de l'icône (QIcon, chemin, ressource, URL, ou SVG)

**Retourne :**
- `QIcon` ou None - Icône chargée ou None si échec

## Exemples d'Intégration

### Interface avec indicateurs de statut

```python
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QHBoxLayout
from ezqt_widgets.label import IndicatorLabel, ClickableTagLabel, HoverLabel

app = QApplication([])
window = QWidget()
layout = QVBoxLayout()

# Section des indicateurs
status_layout = QHBoxLayout()

# Indicateur de statut de service
service_status = IndicatorLabel(
    status_map={
        "running": {"text": "Service actif", "state": "ok", "color": "#28a745"},
        "stopped": {"text": "Service arrêté", "state": "error", "color": "#dc3545"},
        "starting": {"text": "Démarrage...", "state": "warning", "color": "#ffc107"}
    },
    initial_status="running"
)
status_layout.addWidget(service_status)

# Tags de catégories
tags_layout = QHBoxLayout()
python_tag = ClickableTagLabel(name="Python", enabled=True)
qt_tag = ClickableTagLabel(name="Qt", enabled=False)
widgets_tag = ClickableTagLabel(name="Widgets", enabled=True)

tags_layout.addWidget(python_tag)
tags_layout.addWidget(qt_tag)
tags_layout.addWidget(widgets_tag)

# Label avec icône d'aide
help_label = HoverLabel(
    text="Configuration avancée",
    icon="icons/help.png",
    icon_color="#0078d4"
)

layout.addLayout(status_layout)
layout.addLayout(tags_layout)
layout.addWidget(help_label)

window.setLayout(layout)
window.show()
app.exec()
```

### Gestion des événements

```python
# Connexion des signaux pour tous les labels
service_status.statusChanged.connect(lambda status: print(f"Statut du service: {status}"))
python_tag.toggle_keyword.connect(lambda keyword: print(f"Tag sélectionné: {keyword}"))
help_label.hoverIconClicked.connect(lambda: print("Aide demandée"))

# Changement dynamique des statuts
def toggle_service():
    current_status = service_status.status
    if current_status == "running":
        service_status.status = "stopped"
    else:
        service_status.status = "running"

# Simulation d'un changement de statut
import time
import threading

def simulate_status_changes():
    while True:
        time.sleep(5)
        service_status.status = "starting"
        time.sleep(2)
        service_status.status = "running"

threading.Thread(target=simulate_status_changes, daemon=True).start()
```

### Styles personnalisés

```python
# Styles QSS pour les différents widgets
service_status.setStyleSheet("""
    QFrame[state="ok"] {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 4px;
    }
    
    QFrame[state="error"] {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 4px;
    }
    
    QFrame[state="warning"] {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 4px;
    }
""")

# Style pour les tags
python_tag.setStyleSheet("""
    QFrame[enabled="true"] {
        background-color: #0078d4;
        color: white;
        border-radius: 12px;
        padding: 4px 8px;
    }
    
    QFrame[enabled="false"] {
        background-color: #6c757d;
        color: white;
        border-radius: 12px;
        padding: 4px 8px;
    }
""")
```

### Interface de tableau de bord

```python
from PySide6.QtWidgets import QGridLayout, QLabel

# Création d'un tableau de bord avec indicateurs
dashboard = QWidget()
grid_layout = QGridLayout()

# Indicateurs de différents services
services = {
    "Database": IndicatorLabel(initial_status="online"),
    "Web Server": IndicatorLabel(initial_status="running"),
    "Cache": IndicatorLabel(initial_status="offline"),
    "API": IndicatorLabel(initial_status="connecting")
}

# Placement dans la grille
for i, (name, indicator) in enumerate(services.items()):
    label = QLabel(name)
    grid_layout.addWidget(label, i, 0)
    grid_layout.addWidget(indicator, i, 1)

dashboard.setLayout(grid_layout)
layout.addWidget(dashboard)
```

Cette documentation couvre tous les widgets de labels disponibles dans le module `ezqt_widgets.label` avec leurs fonctionnalités, paramètres, propriétés et exemples d'utilisation pratiques. 