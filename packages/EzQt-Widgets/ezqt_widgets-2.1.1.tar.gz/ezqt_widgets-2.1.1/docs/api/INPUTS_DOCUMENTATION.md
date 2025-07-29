# Documentation des Widgets d'Entrée

## Vue d'ensemble

Ce module contient des widgets d'entrée spécialisés qui étendent les fonctionnalités des widgets Qt standard. Ces widgets offrent des fonctionnalités avancées pour la saisie de données, l'autocomplétion, la validation et le traitement de texte.

## Widgets Disponibles

### AutoCompleteInput

**Fichier :** `ezqt_widgets/input/auto_complete_input.py`

**Description :** QLineEdit avec support d'autocomplétion.

**Fonctionnalités :**
- Liste de suggestions pour l'autocomplétion
- Sensibilité à la casse configurable
- Mode de filtrage personnalisable
- Mode de complétion configurable

**Paramètres :**
- `parent` : QWidget, optionnel - Widget parent (défaut : None)
- `suggestions` : List[str], optionnel - Liste de chaînes pour l'autocomplétion (défaut : liste vide)
- `case_sensitive` : bool, optionnel - Si l'autocomplétion est sensible à la casse (défaut : False)
- `filter_mode` : Qt.MatchFlag, optionnel - Mode de filtrage pour la complétion (défaut : Qt.MatchContains)
- `completion_mode` : QCompleter.CompletionMode, optionnel - Mode de complétion (défaut : QCompleter.PopupCompletion)

**Propriétés :**
- `suggestions` : List[str] - Obtenir ou définir la liste de suggestions pour l'autocomplétion
- `case_sensitive` : bool - Obtenir ou définir si l'autocomplétion est sensible à la casse
- `filter_mode` : Qt.MatchFlag - Obtenir ou définir le mode de filtrage pour la complétion
- `completion_mode` : QCompleter.CompletionMode - Obtenir ou définir le mode de complétion

**Méthodes utilitaires :**
- `add_suggestion(suggestion)` - Ajoute une suggestion
- `remove_suggestion(suggestion)` - Supprime une suggestion
- `clear_suggestions()` - Efface toutes les suggestions

**Exemple d'utilisation :**
```python
from ezqt_widgets.input import AutoCompleteInput
from PySide6.QtCore import Qt

# Création d'un champ avec autocomplétion
suggestions = ["Python", "PySide6", "PyQt", "Qt", "Widget", "Application"]
auto_complete = AutoCompleteInput(
    suggestions=suggestions,
    case_sensitive=False,
    filter_mode=Qt.MatchContains
)

# Ajout dynamique de suggestions
auto_complete.add_suggestion("Nouvelle suggestion")
auto_complete.remove_suggestion("PyQt")
```

---

### PasswordInput

**Fichier :** `ezqt_widgets/input/password_input.py`

**Description :** Widget d'entrée de mot de passe amélioré avec barre de force intégrée et icône latérale.

**Fonctionnalités :**
- QLineEdit en mode mot de passe avec barre de force intégrée
- Icône latérale avec fonctionnalité de clic
- Système de gestion d'icônes (QIcon, chemin, URL, SVG)
- Barre de force animée qui remplit la bordure inférieure
- Signal strengthChanged(int) émis lors du changement de mot de passe
- Indicateur de force codé en couleur
- Support de style QSS externe avec variables CSS

**Paramètres :**
- `parent` : QWidget, optionnel - Widget parent (défaut : None)
- `show_strength` : bool, optionnel - Afficher la barre de force du mot de passe (défaut : True)
- `strength_bar_height` : int, optionnel - Hauteur de la barre de force en pixels (défaut : 3)
- `show_icon` : str ou QIcon, optionnel - Icône pour afficher le mot de passe (défaut : icône par défaut)
- `hide_icon` : str ou QIcon, optionnel - Icône pour masquer le mot de passe (défaut : icône par défaut)
- `icon_size` : QSize ou tuple, optionnel - Taille de l'icône (défaut : QSize(16, 16))

**Propriétés :**
- `password` : str - Obtenir ou définir le texte du mot de passe
- `show_strength` : bool - Obtenir ou définir si la barre de force est affichée
- `strength_bar_height` : int - Obtenir ou définir la hauteur de la barre de force
- `show_icon` : QIcon - Obtenir ou définir l'icône d'affichage du mot de passe
- `hide_icon` : QIcon - Obtenir ou définir l'icône de masquage du mot de passe
- `icon_size` : QSize - Obtenir ou définir la taille de l'icône

**Signaux :**
- `strengthChanged(int)` - Émis quand la force du mot de passe change
- `iconClicked()` - Émis quand l'icône est cliquée

**Méthodes utilitaires :**
- `toggle_password()` - Bascule l'affichage/masquage du mot de passe
- `update_strength(text)` - Met à jour la force du mot de passe

**Exemple d'utilisation :**
```python
from ezqt_widgets.input import PasswordInput
from PySide6.QtCore import QSize

# Création d'un champ de mot de passe
password_input = PasswordInput(
    show_strength=True,
    strength_bar_height=4,
    icon_size=QSize(20, 20)
)

# Connexion des signaux
password_input.strengthChanged.connect(lambda strength: print(f"Force: {strength}"))
password_input.iconClicked.connect(lambda: print("Icône cliquée"))

# Définition du mot de passe
password_input.password = "MonMotDePasse123"
```

---

### SearchInput

**Fichier :** `ezqt_widgets/input/search_input.py`

**Description :** QLineEdit pour l'entrée de recherche avec historique intégré et icône de recherche optionnelle.

**Fonctionnalités :**
- Maintient un historique des recherches soumises
- Navigation dans l'historique avec les flèches haut/bas
- Émet un signal searchSubmitted(str) lors de la validation (Entrée)
- Icône de recherche optionnelle (gauche ou droite)
- Bouton d'effacement optionnel

**Paramètres :**
- `parent` : QWidget, optionnel - Widget parent (défaut : None)
- `max_history` : int, optionnel - Nombre maximum d'entrées d'historique à conserver (défaut : 20)
- `search_icon` : QIcon ou str, optionnel - Icône à afficher comme icône de recherche (défaut : None)
- `icon_position` : str, optionnel - 'left' ou 'right' (défaut : 'left')
- `clear_button` : bool, optionnel - Afficher un bouton d'effacement (défaut : True)

**Propriétés :**
- `search_icon` : QIcon - Obtenir ou définir l'icône de recherche
- `icon_position` : str - Obtenir ou définir la position de l'icône ('left' ou 'right')
- `clear_button` : bool - Obtenir ou définir si le bouton d'effacement est affiché
- `max_history` : int - Obtenir ou définir la taille maximale de l'historique

**Signaux :**
- `searchSubmitted(str)` - Émis quand une recherche est soumise (touche Entrée)

**Méthodes utilitaires :**
- `add_to_history(text)` - Ajoute du texte à l'historique
- `get_history()` - Obtient la liste de l'historique
- `clear_history()` - Efface l'historique
- `set_history(history_list)` - Définit l'historique

**Exemple d'utilisation :**
```python
from ezqt_widgets.input import SearchInput

# Création d'un champ de recherche
search_input = SearchInput(
    max_history=50,
    icon_position="left",
    clear_button=True
)

# Connexion du signal
search_input.searchSubmitted.connect(lambda query: print(f"Recherche: {query}"))

# Ajout d'historique
search_input.add_to_history("recherche précédente")
search_input.add_to_history("autre recherche")

# Obtention de l'historique
history = search_input.get_history()
print(f"Historique: {history}")
```

---

### TabReplaceTextEdit

**Fichier :** `ezqt_widgets/input/tab_replace_textedit.py`

**Description :** QPlainTextEdit qui assainit le texte collé en remplaçant les caractères de tabulation selon le mode choisi et en supprimant les lignes vides.

**Fonctionnalités :**
- Remplacement des caractères de tabulation selon le mode choisi
- Suppression des lignes vides lors de l'assainissement
- Utile pour coller des données tabulaires ou assurer une entrée propre

**Paramètres :**
- `parent` : QWidget, optionnel - Widget parent (défaut : None)
- `tab_replacement` : str, optionnel - Chaîne pour remplacer les caractères de tabulation (défaut : "\n")
- `sanitize_on_paste` : bool, optionnel - Assainir le texte collé (défaut : True)
- `remove_empty_lines` : bool, optionnel - Supprimer les lignes vides lors de l'assainissement (défaut : True)
- `preserve_whitespace` : bool, optionnel - Préserver les espaces en début/fin (défaut : False)

**Propriétés :**
- `tab_replacement` : str - Obtenir ou définir la chaîne utilisée pour remplacer les caractères de tabulation
- `sanitize_on_paste` : bool - Activer ou désactiver l'assainissement du texte collé
- `remove_empty_lines` : bool - Obtenir ou définir si les lignes vides sont supprimées
- `preserve_whitespace` : bool - Obtenir ou définir si les espaces sont préservés

**Méthodes utilitaires :**
- `sanitize_text(text)` - Assainit le texte selon les paramètres configurés

**Exemple d'utilisation :**
```python
from ezqt_widgets.input import TabReplaceTextEdit

# Création d'un éditeur de texte avec remplacement de tabulations
text_edit = TabReplaceTextEdit(
    tab_replacement="    ",  # Remplace les tabs par 4 espaces
    sanitize_on_paste=True,
    remove_empty_lines=True,
    preserve_whitespace=False
)

# Assainissement manuel de texte
raw_text = "ligne1\tligne2\n\nligne3\tligne4"
clean_text = text_edit.sanitize_text(raw_text)
print(f"Texte assaini: {clean_text}")
```

## Fonctions Utilitaires

### password_strength(password)

Retourne un score de force de 0 (faible) à 100 (fort).

**Paramètres :**
- `password` : str - Le mot de passe à évaluer

**Retourne :**
- `int` - Score de force du mot de passe

**Critères d'évaluation :**
- Longueur ≥ 8 caractères : +25 points
- Présence de majuscules : +15 points
- Présence de minuscules : +15 points
- Présence de chiffres : +20 points
- Présence de caractères spéciaux : +25 points

### get_strength_color(score)

Retourne une couleur basée sur le score de force du mot de passe.

**Paramètres :**
- `score` : int - Le score de force

**Retourne :**
- `str` - Code couleur hexadécimal

**Échelle de couleurs :**
- < 30 : Rouge (#ff4444)
- < 60 : Orange (#ffaa00)
- < 80 : Vert (#44aa44)
- ≥ 80 : Vert foncé (#00aa00)

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

### Formulaire de connexion complet

```python
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel, QPushButton
from ezqt_widgets.input import AutoCompleteInput, PasswordInput, SearchInput

app = QApplication([])
window = QWidget()
layout = QVBoxLayout()

# Champ de nom d'utilisateur avec autocomplétion
username_label = QLabel("Nom d'utilisateur:")
username_input = AutoCompleteInput(
    suggestions=["admin", "user1", "user2", "guest"],
    placeholder="Entrez votre nom d'utilisateur"
)
layout.addWidget(username_label)
layout.addWidget(username_input)

# Champ de mot de passe
password_label = QLabel("Mot de passe:")
password_input = PasswordInput(
    show_strength=True,
    strength_bar_height=4
)
layout.addWidget(password_label)
layout.addWidget(password_input)

# Bouton de connexion
login_button = QPushButton("Se connecter")
layout.addWidget(login_button)

window.setLayout(layout)
window.show()
app.exec()
```

### Interface de recherche avancée

```python
from PySide6.QtWidgets import QApplication, QHBoxLayout, QWidget, QVBoxLayout
from ezqt_widgets.input import SearchInput, TabReplaceTextEdit

app = QApplication([])
window = QWidget()
layout = QVBoxLayout()

# Barre de recherche
search_layout = QHBoxLayout()
search_input = SearchInput(
    max_history=100,
    icon_position="left",
    clear_button=True
)
search_layout.addWidget(search_input)
layout.addLayout(search_layout)

# Zone de texte pour les résultats
results_edit = TabReplaceTextEdit(
    tab_replacement="  ",  # 2 espaces
    sanitize_on_paste=True,
    remove_empty_lines=False
)
layout.addWidget(results_edit)

window.setLayout(layout)
window.show()
app.exec()
```

### Gestion des événements

```python
# Connexion des signaux pour tous les widgets d'entrée
username_input.textChanged.connect(lambda text: print(f"Nom d'utilisateur: {text}"))
password_input.strengthChanged.connect(lambda strength: print(f"Force du mot de passe: {strength}"))
password_input.iconClicked.connect(lambda: print("Affichage/masquage du mot de passe"))
search_input.searchSubmitted.connect(lambda query: print(f"Recherche soumise: {query}"))
```

### Validation et traitement des données

```python
def validate_form():
    username = username_input.text()
    password = password_input.password
    
    if not username:
        print("Le nom d'utilisateur est requis")
        return False
    
    if len(password) < 8:
        print("Le mot de passe doit contenir au moins 8 caractères")
        return False
    
    print("Formulaire valide")
    return True

# Connexion à la validation
login_button.clicked.connect(validate_form)
```

Cette documentation couvre tous les widgets d'entrée disponibles dans le module `ezqt_widgets.input` avec leurs fonctionnalités, paramètres, propriétés et exemples d'utilisation pratiques. 