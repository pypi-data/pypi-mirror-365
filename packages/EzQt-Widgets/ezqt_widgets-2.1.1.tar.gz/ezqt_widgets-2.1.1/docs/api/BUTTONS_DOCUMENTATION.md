# Documentation des Widgets de Boutons

## Vue d'ensemble

Ce module contient des widgets de boutons spécialisés pour des cas d'usage spécifiques dans les applications Qt. Tous les boutons héritent de `QToolButton` et offrent des fonctionnalités avancées.

## Widgets Disponibles

### DateButton

**Fichier :** `ezqt_widgets/button/date_button.py`

**Description :** Bouton de sélection de date avec calendrier intégré.

**Fonctionnalités :**
- Affichage de la date sélectionnée actuellement
- Ouverture d'une boîte de dialogue calendrier au clic
- Format de date configurable
- Texte d'espace réservé quand aucune date n'est sélectionnée
- Icône de calendrier avec apparence personnalisable
- Validation et analyse de date

**Paramètres :**
- `parent` : QWidget, optionnel - Widget parent (défaut : None)
- `date` : QDate ou str, optionnel - Date initiale (QDate, chaîne de date, ou None pour la date actuelle)
- `date_format` : str, optionnel - Format d'affichage de la date (défaut : "dd/MM/yyyy")
- `placeholder` : str, optionnel - Texte affiché quand aucune date n'est sélectionnée (défaut : "Sélectionner une date")
- `show_calendar_icon` : bool, optionnel - Afficher l'icône de calendrier (défaut : True)
- `icon_size` : QSize ou tuple, optionnel - Taille de l'icône de calendrier (défaut : QSize(16, 16))
- `min_width` : int, optionnel - Largeur minimale du bouton (défaut : None, calculé automatiquement)
- `min_height` : int, optionnel - Hauteur minimale du bouton (défaut : None, calculé automatiquement)

**Propriétés :**
- `date` : QDate - Obtenir ou définir la date sélectionnée
- `date_string` : str - Obtenir ou définir la date sous forme de chaîne formatée
- `date_format` : str - Obtenir ou définir le format de date
- `placeholder` : str - Obtenir ou définir le texte d'espace réservé
- `show_calendar_icon` : bool - Obtenir ou définir la visibilité de l'icône de calendrier
- `icon_size` : QSize - Obtenir ou définir la taille de l'icône
- `min_width` : int - Obtenir ou définir la largeur minimale
- `min_height` : int - Obtenir ou définir la hauteur minimale

**Signaux :**
- `dateChanged(QDate)` - Émis quand la date change
- `dateSelected(QDate)` - Émis quand une date est sélectionnée depuis le calendrier

**Méthodes utilitaires :**
- `clear_date()` - Efface la date sélectionnée
- `set_today()` - Définit la date actuelle
- `open_calendar()` - Ouvre la boîte de dialogue calendrier

**Exemple d'utilisation :**
```python
from ezqt_widgets.button import DateButton
from PySide6.QtCore import QDate

# Création d'un bouton de date
date_button = DateButton(
    date=QDate.currentDate(),
    date_format="dd/MM/yyyy",
    placeholder="Sélectionner une date"
)

# Connexion des signaux
date_button.dateChanged.connect(lambda date: print(f"Date sélectionnée: {date}"))
date_button.dateSelected.connect(lambda date: print(f"Date choisie: {date}"))
```

---

### IconButton

**Fichier :** `ezqt_widgets/button/icon_button.py`

**Description :** Bouton amélioré avec support d'icône et de texte optionnel.

**Fonctionnalités :**
- Support d'icônes depuis diverses sources (QIcon, chemin, URL, SVG)
- Affichage de texte optionnel avec visibilité configurable
- Taille d'icône et espacement personnalisables
- Accès basé sur les propriétés à l'icône et au texte
- Signaux pour les changements d'icône et de texte
- Effets de survol et de clic

**Paramètres :**
- `parent` : QWidget, optionnel - Widget parent (défaut : None)
- `icon` : QIcon ou str, optionnel - Icône à afficher (QIcon, chemin, ressource, URL, ou SVG)
- `text` : str, optionnel - Texte du bouton (défaut : "")
- `icon_size` : QSize ou tuple, optionnel - Taille de l'icône (défaut : QSize(20, 20))
- `text_visible` : bool, optionnel - Si le texte est initialement visible (défaut : True)
- `spacing` : int, optionnel - Espacement entre l'icône et le texte en pixels (défaut : 10)
- `min_width` : int, optionnel - Largeur minimale du bouton (défaut : None, calculé automatiquement)
- `min_height` : int, optionnel - Hauteur minimale du bouton (défaut : None, calculé automatiquement)

**Propriétés :**
- `icon` : QIcon - Obtenir ou définir l'icône du bouton
- `text` : str - Obtenir ou définir le texte du bouton
- `icon_size` : QSize - Obtenir ou définir la taille de l'icône
- `text_visible` : bool - Obtenir ou définir la visibilité du texte
- `spacing` : int - Obtenir ou définir l'espacement entre l'icône et le texte
- `min_width` : int - Obtenir ou définir la largeur minimale du bouton
- `min_height` : int - Obtenir ou définir la hauteur minimale du bouton

**Signaux :**
- `iconChanged(QIcon)` - Émis quand l'icône change
- `textChanged(str)` - Émis quand le texte change

**Méthodes utilitaires :**
- `clear_icon()` - Efface l'icône
- `clear_text()` - Efface le texte
- `toggle_text_visibility()` - Bascule la visibilité du texte
- `set_icon_color(color, opacity)` - Applique une couleur à l'icône

**Exemple d'utilisation :**
```python
from ezqt_widgets.button import IconButton

# Création d'un bouton avec icône
icon_button = IconButton(
    icon="path/to/icon.png",
    text="Mon Bouton",
    icon_size=(24, 24),
    text_visible=True
)

# Connexion des signaux
icon_button.iconChanged.connect(lambda icon: print("Icône changée"))
icon_button.textChanged.connect(lambda text: print(f"Texte changé: {text}"))

# Méthodes utilitaires
icon_button.set_icon_color("#0078d4", 0.8)
icon_button.toggle_text_visibility()
```

---

### LoaderButton

**Fichier :** `ezqt_widgets/button/loader_button.py`

**Description :** Bouton avec animation de chargement intégrée.

**Fonctionnalités :**
- État de chargement avec spinner animé
- État de succès avec icône de coche
- État d'erreur avec icône X
- Texte et icônes de chargement, succès et erreur configurables
- Transitions fluides entre les états
- État désactivé pendant le chargement
- Vitesse d'animation personnalisable
- Support d'indication de progression
- Réinitialisation automatique après achèvement avec temps d'affichage configurables

**Paramètres :**
- `parent` : QWidget, optionnel - Widget parent (défaut : None)
- `text` : str, optionnel - Texte du bouton (défaut : "")
- `icon` : QIcon ou str, optionnel - Icône du bouton (défaut : None)
- `loading_text` : str, optionnel - Texte affiché pendant le chargement (défaut : "Chargement...")
- `loading_icon` : QIcon ou str, optionnel - Icône affichée pendant le chargement (défaut : None, généré automatiquement)
- `success_icon` : QIcon ou str, optionnel - Icône affichée en cas de succès (défaut : None, coche générée automatiquement)
- `error_icon` : QIcon ou str, optionnel - Icône affichée en cas d'erreur (défaut : None, X généré automatiquement)
- `animation_speed` : int, optionnel - Vitesse d'animation en millisecondes (défaut : 100)
- `auto_reset` : bool, optionnel - Réinitialisation automatique après chargement (défaut : True)
- `success_display_time` : int, optionnel - Temps d'affichage de l'état de succès en millisecondes (défaut : 1000)
- `error_display_time` : int, optionnel - Temps d'affichage de l'état d'erreur en millisecondes (défaut : 2000)
- `min_width` : int, optionnel - Largeur minimale du bouton (défaut : None, calculé automatiquement)
- `min_height` : int, optionnel - Hauteur minimale du bouton (défaut : None, calculé automatiquement)

**Propriétés :**
- `text` : str - Obtenir ou définir le texte du bouton
- `icon` : QIcon - Obtenir ou définir l'icône du bouton
- `loading_text` : str - Obtenir ou définir le texte de chargement
- `loading_icon` : QIcon - Obtenir ou définir l'icône de chargement
- `success_icon` : QIcon - Obtenir ou définir l'icône de succès
- `error_icon` : QIcon - Obtenir ou définir l'icône d'erreur
- `is_loading` : bool - Obtenir l'état de chargement actuel
- `animation_speed` : int - Obtenir ou définir la vitesse d'animation
- `auto_reset` : bool - Obtenir ou définir le comportement de réinitialisation automatique
- `success_display_time` : int - Obtenir ou définir le temps d'affichage de succès
- `error_display_time` : int - Obtenir ou définir le temps d'affichage d'erreur
- `min_width` : int - Obtenir ou définir la largeur minimale
- `min_height` : int - Obtenir ou définir la hauteur minimale

**Signaux :**
- `loadingStarted()` - Émis quand le chargement commence
- `loadingFinished()` - Émis quand le chargement se termine avec succès
- `loadingFailed(str)` - Émis quand le chargement échoue avec un message d'erreur

**Méthodes utilitaires :**
- `start_loading()` - Démarre l'animation de chargement
- `stop_loading(success, error_message)` - Arrête le chargement avec succès ou erreur

**Exemple d'utilisation :**
```python
from ezqt_widgets.button import LoaderButton
import time
import threading

# Création d'un bouton de chargement
loader_button = LoaderButton(
    text="Télécharger",
    loading_text="Téléchargement en cours...",
    animation_speed=150
)

# Connexion des signaux
loader_button.loadingStarted.connect(lambda: print("Chargement démarré"))
loader_button.loadingFinished.connect(lambda: print("Chargement terminé"))
loader_button.loadingFailed.connect(lambda msg: print(f"Erreur: {msg}"))

# Simulation d'une tâche de chargement
def simulate_loading():
    loader_button.start_loading()
    time.sleep(3)  # Simulation d'un travail
    loader_button.stop_loading(success=True)

# Démarrage du chargement dans un thread séparé
threading.Thread(target=simulate_loading, daemon=True).start()
```

## Fonctions Utilitaires

### format_date(date, format_str)

Formate un objet QDate en chaîne de caractères.

**Paramètres :**
- `date` : QDate - La date à formater
- `format_str` : str, optionnel - Chaîne de format (défaut : "dd/MM/yyyy")

**Retourne :**
- `str` - Chaîne de date formatée

### parse_date(date_str, format_str)

Analyse une chaîne de date en objet QDate.

**Paramètres :**
- `date_str` : str - La chaîne de date à analyser
- `format_str` : str, optionnel - Chaîne de format (défaut : "dd/MM/yyyy")

**Retourne :**
- `QDate` - Objet QDate analysé ou QDate invalide si l'analyse échoue

### get_calendar_icon()

Obtient une icône de calendrier par défaut.

**Retourne :**
- `QIcon` - Icône de calendrier

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

### create_spinner_pixmap(size, color)

Crée un pixmap de spinner pour l'animation de chargement.

**Paramètres :**
- `size` : int, optionnel - Taille du spinner (défaut : 16)
- `color` : str, optionnel - Couleur du spinner (défaut : "#0078d4")

**Retourne :**
- `QPixmap` - Pixmap du spinner

### create_loading_icon(size, color)

Crée une icône de chargement avec spinner.

**Paramètres :**
- `size` : int, optionnel - Taille de l'icône (défaut : 16)
- `color` : str, optionnel - Couleur de l'icône (défaut : "#0078d4")

**Retourne :**
- `QIcon` - Icône de chargement

### create_success_icon(size, color)

Crée une icône de succès avec coche.

**Paramètres :**
- `size` : int, optionnel - Taille de l'icône (défaut : 16)
- `color` : str, optionnel - Couleur de l'icône (défaut : "#28a745")

**Retourne :**
- `QIcon` - Icône de succès

### create_error_icon(size, color)

Crée une icône d'erreur avec X.

**Paramètres :**
- `size` : int, optionnel - Taille de l'icône (défaut : 16)
- `color` : str, optionnel - Couleur de l'icône (défaut : "#dc3545")

**Retourne :**
- `QIcon` - Icône d'erreur

## Exemples d'Intégration

### Interface avec plusieurs types de boutons

```python
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QHBoxLayout
from ezqt_widgets.button import DateButton, IconButton, LoaderButton

app = QApplication([])
window = QWidget()
layout = QVBoxLayout()

# Section des boutons
button_layout = QHBoxLayout()

# Bouton de date
date_button = DateButton(placeholder="Date de début")
button_layout.addWidget(date_button)

# Bouton avec icône
icon_button = IconButton(
    icon="icons/save.png",
    text="Sauvegarder",
    icon_size=(20, 20)
)
button_layout.addWidget(icon_button)

# Bouton de chargement
loader_button = LoaderButton(
    text="Traiter",
    loading_text="Traitement en cours..."
)
button_layout.addWidget(loader_button)

layout.addLayout(button_layout)
window.setLayout(layout)
window.show()
app.exec()
```

### Gestion des événements

```python
# Connexion des signaux pour tous les boutons
date_button.dateChanged.connect(lambda date: print(f"Date sélectionnée: {date}"))
icon_button.clicked.connect(lambda: print("Bouton icône cliqué"))
loader_button.loadingStarted.connect(lambda: print("Traitement démarré"))
loader_button.loadingFinished.connect(lambda: print("Traitement terminé"))
```

Cette documentation couvre tous les widgets de boutons disponibles dans le module `ezqt_widgets.button` avec leurs fonctionnalités, paramètres, propriétés et exemples d'utilisation. 