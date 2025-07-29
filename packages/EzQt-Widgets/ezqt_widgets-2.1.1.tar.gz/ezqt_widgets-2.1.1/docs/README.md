# Documentation Technique EzQt Widgets

## Vue d'ensemble

Cette documentation présente la bibliothèque **EzQt Widgets**, une collection de widgets Qt spécialisés conçus pour simplifier le développement d'interfaces graphiques modernes et intuitives.

## Structure de la Documentation

### 📚 Documentation Générale
- **[README.md](README.md)** - Ce fichier, guide d'utilisation de la documentation

### 🎯 Documentation de l'API
- **[api/README.md](api/README.md)** - Guide de la documentation de l'API
- **[api/WIDGETS_DOCUMENTATION.md](api/WIDGETS_DOCUMENTATION.md)** - Vue d'ensemble complète de tous les widgets
- **[api/BUTTONS_DOCUMENTATION.md](api/BUTTONS_DOCUMENTATION.md)** - Widgets de boutons spécialisés
- **[api/INPUTS_DOCUMENTATION.md](api/INPUTS_DOCUMENTATION.md)** - Widgets d'entrée avancés
- **[api/LABELS_DOCUMENTATION.md](api/LABELS_DOCUMENTATION.md)** - Widgets de labels interactifs
- **[api/MISC_DOCUMENTATION.md](api/MISC_DOCUMENTATION.md)** - Widgets divers et utilitaires
- **[api/STYLE_GUIDE.md](api/STYLE_GUIDE.md)** - Guide de style et bonnes pratiques

### 🧪 Documentation des Tests
- **[tests/](tests/)** - Documentation spécifique aux tests
- **[tests/QUICK_START_TESTS.md](tests/QUICK_START_TESTS.md)** - Guide de démarrage rapide pour les tests

## Widgets Disponibles

### 🎛️ Widgets de Boutons
| Widget | Description | Fichier |
|--------|-------------|---------|
| **DateButton** | Bouton de sélection de date avec calendrier intégré | `button/date_button.py` |
| **IconButton** | Bouton avec support d'icône et texte optionnel | `button/icon_button.py` |
| **LoaderButton** | Bouton avec animation de chargement intégrée | `button/loader_button.py` |

### ⌨️ Widgets d'Entrée
| Widget | Description | Fichier |
|--------|-------------|---------|
| **AutoCompleteInput** | Champ de texte avec autocomplétion | `input/auto_complete_input.py` |
| **PasswordInput** | Champ de mot de passe avec indicateur de force | `input/password_input.py` |
| **SearchInput** | Champ de recherche avec historique | `input/search_input.py` |
| **TabReplaceTextEdit** | Éditeur de texte avec remplacement de tabulations | `input/tab_replace_textedit.py` |

### 🏷️ Widgets de Labels
| Widget | Description | Fichier |
|--------|-------------|---------|
| **ClickableTagLabel** | Tag cliquable avec état basculable | `label/clickable_tag_label.py` |
| **FramedLabel** | Label encadré pour le style avancé | `label/framed_label.py` |
| **HoverLabel** | Label avec icône au survol | `label/hover_label.py` |
| **IndicatorLabel** | Indicateur de statut avec LED colorée | `label/indicator_label.py` |

### 🔧 Widgets Divers
| Widget | Description | Fichier |
|--------|-------------|---------|
| **CircularTimer** | Timer circulaire animé | `misc/circular_timer.py` |
| **OptionSelector** | Sélecteur d'options avec animation | `misc/option_selector.py` |
| **ToggleIcon** | Icône basculable ouvert/fermé | `misc/toggle_icon.py` |
| **ToggleSwitch** | Commutateur moderne avec animation | `misc/toggle_switch.py` |

## Installation et Utilisation

### Installation
```bash
pip install ezqt-widgets
```

### Import des Widgets
```python
# Import des widgets de boutons
from ezqt_widgets.button import DateButton, IconButton, LoaderButton

# Import des widgets d'entrée
from ezqt_widgets.input import AutoCompleteInput, PasswordInput, SearchInput, TabReplaceTextEdit

# Import des widgets de labels
from ezqt_widgets.label import ClickableTagLabel, FramedLabel, HoverLabel, IndicatorLabel

# Import des widgets divers
from ezqt_widgets.misc import CircularTimer, OptionSelector, ToggleIcon, ToggleSwitch
```

### Exemple d'Utilisation Rapide
```python
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
from ezqt_widgets.button import DateButton, IconButton
from ezqt_widgets.input import PasswordInput
from ezqt_widgets.misc import ToggleSwitch

app = QApplication([])
window = QWidget()
layout = QVBoxLayout()

# Création des widgets
date_button = DateButton(placeholder="Sélectionner une date")
icon_button = IconButton(text="Mon Bouton", icon="path/to/icon.png")
password_input = PasswordInput(show_strength=True)
toggle = ToggleSwitch(checked=True)

# Ajout au layout
layout.addWidget(date_button)
layout.addWidget(icon_button)
layout.addWidget(password_input)
layout.addWidget(toggle)

window.setLayout(layout)
window.show()
app.exec()
```

## Fonctionnalités Principales

### ✨ Caractéristiques Générales
- **Compatibilité PySide6** : Tous les widgets sont basés sur PySide6
- **Type Hints** : Support complet des annotations de type
- **Signaux Qt** : Intégration native avec le système de signaux Qt
- **Styles QSS** : Support complet des feuilles de style Qt
- **Accessibilité** : Support des fonctionnalités d'accessibilité

### 🎨 Personnalisation
- **Propriétés** : Accès basé sur les propriétés pour tous les paramètres
- **Styles** : Personnalisation via QSS avec variables CSS
- **Thèmes** : Support des thèmes sombres et clairs
- **Animations** : Animations fluides et configurables

### 🔧 Extensibilité
- **Héritage** : Tous les widgets peuvent être étendus
- **Composition** : Combinaison facile de plusieurs widgets
- **Signaux personnalisés** : Ajout de signaux spécifiques
- **Méthodes utilitaires** : Fonctions d'aide intégrées

## Exemples d'Intégration

### Interface de Connexion
```python
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel, QPushButton
from ezqt_widgets.input import AutoCompleteInput, PasswordInput

app = QApplication([])
window = QWidget()
layout = QVBoxLayout()

# Champ de nom d'utilisateur avec autocomplétion
username_input = AutoCompleteInput(
    suggestions=["admin", "user1", "user2", "guest"],
    placeholder="Nom d'utilisateur"
)

# Champ de mot de passe avec indicateur de force
password_input = PasswordInput(
    show_strength=True,
    strength_bar_height=4
)

# Bouton de connexion
login_button = QPushButton("Se connecter")

layout.addWidget(QLabel("Nom d'utilisateur:"))
layout.addWidget(username_input)
layout.addWidget(QLabel("Mot de passe:"))
layout.addWidget(password_input)
layout.addWidget(login_button)

window.setLayout(layout)
window.show()
app.exec()
```

### Tableau de Bord
```python
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QHBoxLayout
from ezqt_widgets.label import IndicatorLabel, ClickableTagLabel
from ezqt_widgets.misc import CircularTimer, ToggleSwitch

app = QApplication([])
window = QWidget()
layout = QVBoxLayout()

# Indicateurs de statut
status_layout = QHBoxLayout()
service_status = IndicatorLabel(
    status_map={
        "running": {"text": "Service actif", "state": "ok", "color": "#28a745"},
        "stopped": {"text": "Service arrêté", "state": "error", "color": "#dc3545"}
    },
    initial_status="running"
)
status_layout.addWidget(service_status)

# Tags de catégories
tags_layout = QHBoxLayout()
python_tag = ClickableTagLabel(name="Python", enabled=True)
qt_tag = ClickableTagLabel(name="Qt", enabled=False)
tags_layout.addWidget(python_tag)
tags_layout.addWidget(qt_tag)

# Contrôles
controls_layout = QHBoxLayout()
timer = CircularTimer(duration=5000, loop=True)
switch = ToggleSwitch(checked=True)
controls_layout.addWidget(timer)
controls_layout.addWidget(switch)

layout.addLayout(status_layout)
layout.addLayout(tags_layout)
layout.addLayout(controls_layout)

window.setLayout(layout)
window.show()
app.exec()
```

## Bonnes Pratiques

### 🎯 Utilisation des Widgets
1. **Importez spécifiquement** les widgets dont vous avez besoin
2. **Utilisez les propriétés** pour modifier les widgets après création
3. **Connectez les signaux** pour réagir aux événements utilisateur
4. **Personnalisez les styles** avec QSS pour une apparence cohérente

### 🎨 Styling
```python
# Style personnalisé pour un widget
widget.setStyleSheet("""
    QWidget {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 5px;
    }
    
    QWidget:hover {
        background-color: #3d3d3d;
        border-color: #0078d4;
    }
""")
```

### 🔧 Gestion des Événements
```python
# Connexion des signaux
date_button.dateChanged.connect(lambda date: print(f"Date sélectionnée: {date}"))
password_input.strengthChanged.connect(lambda strength: print(f"Force: {strength}"))
toggle.toggled.connect(lambda checked: print(f"Commutateur: {checked}"))
```

## Support et Contribution

### 📖 Documentation
- **Documentation complète** : Chaque widget est documenté avec exemples
- **Code source** : Tous les widgets sont open source et commentés
- **Tests** : Suite de tests complète pour chaque widget

### 🐛 Problèmes et Améliorations
- **Issues** : Signalez les problèmes sur le repository GitHub
- **Pull Requests** : Contributions bienvenues pour améliorer les widgets
- **Discussions** : Échangez avec la communauté sur les forums

### 📚 Ressources Supplémentaires
- **Exemples** : Dossier `examples/` avec des cas d'usage complets
- **Tests** : Dossier `tests/` avec des tests unitaires et d'intégration
- **Changelog** : Historique des versions et nouvelles fonctionnalités

## Licence

Cette bibliothèque est distribuée sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

**EzQt Widgets** - Simplifiez le développement d'interfaces Qt modernes et intuitives. 