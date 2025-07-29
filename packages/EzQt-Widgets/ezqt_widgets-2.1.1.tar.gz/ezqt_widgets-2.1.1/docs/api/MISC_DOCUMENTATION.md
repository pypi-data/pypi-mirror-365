# Documentation des Widgets Divers

## Vue d'ensemble

Ce module contient des widgets spécialisés qui ne rentrent pas dans les catégories principales (boutons, entrées, labels). Ces widgets offrent des fonctionnalités avancées pour les animations, les sélections, les indicateurs visuels et les contrôles interactifs.

## Widgets Disponibles

### CircularTimer

**Fichier :** `ezqt_widgets/misc/circular_timer.py`

**Description :** Timer circulaire animé pour indiquer une progression ou un temps écoulé.

**Fonctionnalités :**
- Animation circulaire de progression
- Couleurs personnalisables pour l'arc et le centre
- Modes d'épaisseur d'arc configurables
- Boucle automatique optionnelle
- Signaux pour les événements de cycle

**Paramètres :**
- `parent` : QWidget, optionnel - Parent Qt (défaut : None)
- `duration` : int, optionnel - Durée totale de l'animation en millisecondes (défaut : 5000)
- `ring_color` : QColor | str, optionnel - Couleur de l'arc de progression (défaut : #0078d4)
- `node_color` : QColor | str, optionnel - Couleur du centre (défaut : #2d2d2d)
- `ring_width_mode` : str, optionnel - "small", "medium" (défaut), ou "large"
- `pen_width` : int | float, optionnel - Épaisseur de l'arc (prioritaire sur ring_width_mode si défini)
- `loop` : bool, optionnel - Si True, le timer boucle automatiquement à chaque cycle (défaut : False)

**Propriétés :**
- `duration` : int - Durée totale de l'animation
- `elapsed` : int - Temps écoulé depuis le début de l'animation
- `running` : bool - Indique si le timer est en cours d'animation
- `ring_color` : QColor - Couleur de l'arc de progression
- `node_color` : QColor - Couleur du centre
- `ring_width_mode` : str - "small", "medium", "large"
- `pen_width` : float - Épaisseur de l'arc (prioritaire sur ring_width_mode)
- `loop` : bool - Si True, le timer boucle automatiquement à chaque cycle

**Signaux :**
- `timerReset()` - Émis lorsque le timer est réinitialisé
- `clicked()` - Émis lors d'un clic sur le widget
- `cycleCompleted()` - Émis à chaque fin de cycle (même si loop=False)

**Méthodes utilitaires :**
- `startTimer()` - Démarre le timer
- `stopTimer()` - Arrête le timer
- `resetTimer()` - Réinitialise le timer

**Exemple d'utilisation :**
```python
from ezqt_widgets.misc import CircularTimer

# Création d'un timer circulaire
timer = CircularTimer(
    duration=10000,  # 10 secondes
    ring_color="#0078d4",
    node_color="#ffffff",
    ring_width_mode="medium",
    loop=True
)

# Connexion des signaux
timer.timerReset.connect(lambda: print("Timer réinitialisé"))
timer.clicked.connect(lambda: print("Timer cliqué"))
timer.cycleCompleted.connect(lambda: print("Cycle terminé"))

# Démarrage du timer
timer.startTimer()

# Arrêt après 5 secondes
import time
time.sleep(5)
timer.stopTimer()
```

---

### OptionSelector

**Fichier :** `ezqt_widgets/misc/option_selector.py`

**Description :** Widget de sélection d'options avec sélecteur animé.

**Fonctionnalités :**
- Plusieurs options sélectionnables affichées comme des labels
- Sélecteur animé qui se déplace entre les options
- Mode de sélection unique (comportement radio)
- Sélection par défaut configurable par ID (index)
- Animations fluides avec courbes d'accélération
- Événements de clic pour la sélection d'options
- Utilise des IDs en interne pour une gestion robuste des valeurs

**Paramètres :**
- `items` : List[str] - Liste des textes d'options à afficher
- `default_id` : int, optionnel - ID d'option sélectionnée par défaut (index) (défaut : 0)
- `min_width` : int, optionnel - Contrainte de largeur minimale pour le widget (défaut : None)
- `min_height` : int, optionnel - Contrainte de hauteur minimale pour le widget (défaut : None)
- `orientation` : str, optionnel - Orientation de mise en page : "horizontal" ou "vertical" (défaut : "horizontal")
- `animation_duration` : int, optionnel - Durée de l'animation du sélecteur en millisecondes (défaut : 300)
- `parent` : QWidget, optionnel - Widget parent (défaut : None)

**Propriétés :**
- `value` : str - Obtenir ou définir l'option actuellement sélectionnée
- `value_id` : int - Obtenir ou définir l'ID de l'option actuellement sélectionnée
- `options` : List[str] - Obtenir la liste des options disponibles
- `default_id` : int - Obtenir ou définir l'ID de l'option par défaut
- `selected_option` : FramedLabel - Obtenir le widget d'option actuellement sélectionné
- `orientation` : str - Obtenir ou définir l'orientation de mise en page ("horizontal" ou "vertical")
- `min_width` : int - Obtenir ou définir la contrainte de largeur minimale
- `min_height` : int - Obtenir ou définir la contrainte de hauteur minimale
- `animation_duration` : int - Obtenir ou définir la durée d'animation en millisecondes

**Signaux :**
- `clicked()` - Émis quand une option est cliquée
- `valueChanged(str)` - Émis quand la valeur sélectionnée change
- `valueIdChanged(int)` - Émis quand l'ID de valeur sélectionnée change

**Méthodes utilitaires :**
- `initialize_selector(default_id)` - Initialise le sélecteur
- `add_option(option_id, option_text)` - Ajoute une option
- `toggle_selection(option_id)` - Bascule la sélection d'une option

**Exemple d'utilisation :**
```python
from ezqt_widgets.misc import OptionSelector

# Création d'un sélecteur d'options
options = ["Option 1", "Option 2", "Option 3", "Option 4"]
selector = OptionSelector(
    items=options,
    default_id=1,
    orientation="horizontal",
    animation_duration=500
)

# Connexion des signaux
selector.clicked.connect(lambda: print("Option cliquée"))
selector.valueChanged.connect(lambda value: print(f"Valeur sélectionnée: {value}"))
selector.valueIdChanged.connect(lambda id: print(f"ID sélectionné: {id}"))

# Changement de sélection
selector.value = "Option 3"
selector.value_id = 2
```

---

### ToggleIcon

**Fichier :** `ezqt_widgets/misc/toggle_icon.py`

**Description :** Label avec icônes basculables pour indiquer un état ouvert/fermé.

**Fonctionnalités :**
- Icônes pour les états ouvert et fermé
- Basculement d'état au clic
- Couleurs personnalisables
- Support de différentes sources d'icônes

**Paramètres :**
- `parent` : QWidget, optionnel - Parent Qt (défaut : None)
- `opened_icon` : str | QIcon | QPixmap, optionnel - Icône à afficher quand l'état est "opened"
- `closed_icon` : str | QIcon | QPixmap, optionnel - Icône à afficher quand l'état est "closed"
- `icon_size` : int, optionnel - Taille des icônes en pixels (défaut : 16)
- `icon_color` : QColor | str, optionnel - Couleur à appliquer aux icônes (défaut : blanc avec 0.5 opacité)
- `initial_state` : str, optionnel - État initial ("opened" ou "closed", défaut : "closed")
- `min_width` : int, optionnel - Largeur minimale du widget
- `min_height` : int, optionnel - Hauteur minimale du widget

**Propriétés :**
- `state` : str - État actuel ("opened" ou "closed")
- `opened_icon` : QPixmap - Icône de l'état ouvert
- `closed_icon` : QPixmap - Icône de l'état fermé
- `icon_size` : int - Taille des icônes
- `icon_color` : QColor - Couleur des icônes
- `min_width` : int - Largeur minimale
- `min_height` : int - Hauteur minimale

**Signaux :**
- `stateChanged(str)` - Émis quand l'état change ("opened" ou "closed")
- `clicked()` - Émis lors d'un clic sur le widget

**Méthodes utilitaires :**
- `toggle_state()` - Bascule l'état
- `set_state_opened()` - Définit l'état ouvert
- `set_state_closed()` - Définit l'état fermé
- `is_opened()` - Vérifie si l'état est ouvert
- `is_closed()` - Vérifie si l'état est fermé

**Exemple d'utilisation :**
```python
from ezqt_widgets.misc import ToggleIcon

# Création d'un icône basculable
toggle_icon = ToggleIcon(
    opened_icon="icons/chevron-down.png",
    closed_icon="icons/chevron-right.png",
    icon_size=20,
    icon_color="#0078d4",
    initial_state="closed"
)

# Connexion des signaux
toggle_icon.stateChanged.connect(lambda state: print(f"État changé: {state}"))
toggle_icon.clicked.connect(lambda: print("Icône cliquée"))

# Basculement de l'état
toggle_icon.toggle_state()
toggle_icon.set_state_opened()
toggle_icon.set_state_closed()

# Vérification de l'état
if toggle_icon.is_opened():
    print("L'icône est ouverte")
```

---

### ToggleSwitch

**Fichier :** `ezqt_widgets/misc/toggle_switch.py`

**Description :** Widget de commutateur moderne avec cercle glissant animé.

**Fonctionnalités :**
- Animation fluide lors du basculement
- Couleurs personnalisables pour les états activé/désactivé
- Taille et rayon de bordure configurables
- Fonctionnalité de basculement au clic
- Accès basé sur les propriétés à l'état
- Signal émis lors du changement d'état

**Paramètres :**
- `parent` : QWidget, optionnel - Widget parent (défaut : None)
- `checked` : bool, optionnel - État initial du commutateur (défaut : False)
- `width` : int, optionnel - Largeur du commutateur (défaut : 50)
- `height` : int, optionnel - Hauteur du commutateur (défaut : 24)
- `animation` : bool, optionnel - Animer le basculement (défaut : True)

**Propriétés :**
- `checked` : bool - Obtenir ou définir l'état du commutateur
- `width` : int - Obtenir ou définir la largeur du commutateur
- `height` : int - Obtenir ou définir la hauteur du commutateur
- `animation` : bool - Obtenir ou définir si l'animation est activée

**Signaux :**
- `toggled(bool)` - Émis quand l'état du commutateur change

**Méthodes utilitaires :**
- `toggle()` - Bascule l'état du commutateur

**Exemple d'utilisation :**
```python
from ezqt_widgets.misc import ToggleSwitch

# Création d'un commutateur
toggle_switch = ToggleSwitch(
    checked=False,
    width=60,
    height=30,
    animation=True
)

# Connexion du signal
toggle_switch.toggled.connect(lambda checked: print(f"Commutateur: {checked}"))

# Basculement
toggle_switch.toggle()
toggle_switch.checked = True
```

## Fonctions Utilitaires

### parse_css_color(color_str)

Analyse les chaînes de couleur CSS (rgb, rgba, hex, couleurs nommées) en QColor.

**Paramètres :**
- `color_str` : Union[QColor, str] - La couleur à analyser

**Retourne :**
- `QColor` - Objet QColor

**Formats supportés :**
- `rgb(r, g, b)` - Couleurs RGB
- `rgba(r, g, b, a)` - Couleurs RGBA avec transparence
- Codes hexadécimaux (#ff0000)
- Couleurs nommées (red, blue, etc.)

### colorize_pixmap(pixmap, color)

Applique une couleur à un QPixmap avec opacité.

**Paramètres :**
- `pixmap` : QPixmap - Le pixmap à colorer
- `color` : QColor - La couleur à appliquer

**Retourne :**
- `QPixmap` - Le pixmap coloré

### load_icon_from_source(source, size)

Charge une icône depuis différentes sources (chemin, URL, QIcon, QPixmap).

**Paramètres :**
- `source` : Union[str, QIcon, QPixmap] - Source de l'icône
- `size` : QSize, optionnel - Taille souhaitée pour l'icône

**Retourne :**
- `QPixmap` - Le pixmap de l'icône chargée

## Exemples d'Intégration

### Interface de contrôle avec plusieurs widgets

```python
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QHBoxLayout, QLabel
from ezqt_widgets.misc import CircularTimer, OptionSelector, ToggleIcon, ToggleSwitch

app = QApplication([])
window = QWidget()
layout = QVBoxLayout()

# Section des contrôles
controls_layout = QHBoxLayout()

# Timer circulaire
timer_label = QLabel("Progression:")
timer = CircularTimer(duration=5000, loop=True)
controls_layout.addWidget(timer_label)
controls_layout.addWidget(timer)

# Sélecteur d'options
selector_label = QLabel("Mode:")
selector = OptionSelector(
    items=["Automatique", "Manuel", "Test"],
    default_id=0
)
controls_layout.addWidget(selector_label)
controls_layout.addWidget(selector)

# Icône basculable
toggle_icon = ToggleIcon(
    opened_icon="icons/expand.png",
    closed_icon="icons/collapse.png"
)
controls_layout.addWidget(toggle_icon)

# Commutateur
switch_label = QLabel("Activer:")
switch = ToggleSwitch(checked=True)
controls_layout.addWidget(switch_label)
controls_layout.addWidget(switch)

layout.addLayout(controls_layout)
window.setLayout(layout)
window.show()
app.exec()
```

### Gestion des événements

```python
# Connexion des signaux pour tous les widgets
timer.cycleCompleted.connect(lambda: print("Timer terminé"))
selector.valueChanged.connect(lambda value: print(f"Mode sélectionné: {value}"))
toggle_icon.stateChanged.connect(lambda state: print(f"État icône: {state}"))
switch.toggled.connect(lambda checked: print(f"Commutateur: {checked}"))

# Démarrage du timer
timer.startTimer()

# Changement de sélection
selector.value = "Manuel"
toggle_icon.toggle_state()
switch.toggle()
```

### Interface de configuration

```python
from PySide6.QtWidgets import QGroupBox, QFormLayout

# Création d'un groupe de configuration
config_group = QGroupBox("Configuration")
config_layout = QFormLayout()

# Options de configuration
config_options = {
    "Mode de fonctionnement": OptionSelector(["Normal", "Économique", "Performance"]),
    "Notifications": ToggleSwitch(checked=True),
    "Sauvegarde automatique": ToggleSwitch(checked=False),
    "Mode debug": ToggleSwitch(checked=False)
}

# Ajout des options au formulaire
for label, widget in config_options.items():
    config_layout.addRow(label, widget)

config_group.setLayout(config_layout)
layout.addWidget(config_group)
```

### Interface de monitoring

```python
from PySide6.QtWidgets import QGridLayout

# Création d'un tableau de monitoring
monitoring = QWidget()
grid_layout = QGridLayout()

# Services avec indicateurs
services = {
    "Service A": {
        "status": ToggleSwitch(checked=True),
        "timer": CircularTimer(duration=3000, loop=True),
        "mode": OptionSelector(["Actif", "En attente", "Arrêté"])
    },
    "Service B": {
        "status": ToggleSwitch(checked=False),
        "timer": CircularTimer(duration=5000, loop=True),
        "mode": OptionSelector(["Actif", "En attente", "Arrêté"])
    }
}

# Placement dans la grille
for i, (service_name, widgets) in enumerate(services.items()):
    grid_layout.addWidget(QLabel(service_name), i, 0)
    grid_layout.addWidget(widgets["status"], i, 1)
    grid_layout.addWidget(widgets["timer"], i, 2)
    grid_layout.addWidget(widgets["mode"], i, 3)

monitoring.setLayout(grid_layout)
layout.addWidget(monitoring)
```

### Styles personnalisés

```python
# Styles QSS pour les widgets
timer.setStyleSheet("""
    QWidget {
        background-color: transparent;
    }
""")

selector.setStyleSheet("""
    QFrame {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 4px;
    }
    
    QFrame[selected="true"] {
        background-color: #0078d4;
        color: white;
    }
""")

toggle_icon.setStyleSheet("""
    QLabel {
        background-color: transparent;
        border: none;
    }
    
    QLabel:hover {
        background-color: #f8f9fa;
        border-radius: 4px;
    }
""")

switch.setStyleSheet("""
    QWidget {
        background-color: #6c757d;
        border-radius: 12px;
    }
""")
```

Cette documentation couvre tous les widgets divers disponibles dans le module `ezqt_widgets.misc` avec leurs fonctionnalités, paramètres, propriétés et exemples d'utilisation pratiques. 