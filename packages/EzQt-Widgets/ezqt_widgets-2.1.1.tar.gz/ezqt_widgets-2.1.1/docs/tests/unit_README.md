# Tests Unitaires - Vue d'ensemble

## Vue d'ensemble

Ce document fournit une vue d'ensemble des tests unitaires pour le package `ezqt_widgets`.

## Structure des Tests

```
tests/
├── unit/
│   ├── test_button/
│   │   ├── test_date_button.py
│   │   ├── test_icon_button.py
│   │   └── test_loader_button.py
│   ├── test_input/
│   │   ├── test_auto_complete_input.py
│   │   ├── test_password_input.py
│   │   ├── test_search_input.py
│   │   └── test_tab_replace_textedit.py
│   ├── test_label/
│   │   ├── test_clickable_tag_label.py
│   │   ├── test_framed_label.py
│   │   ├── test_hover_label.py
│   │   └── test_indicator_label.py
│   └── test_misc/
│       ├── test_circular_timer.py
│       ├── test_option_selector.py
│       ├── test_toggle_icon.py
│       └── test_toggle_switch.py
├── conftest.py
└── run_tests.py
```

## Catégories de Widgets Testés

### 1. Widgets Button
- **DateButton** : Bouton de sélection de date
- **IconButton** : Bouton avec icône
- **LoaderButton** : Bouton avec indicateur de chargement

**Documentation :** [test_button_README.md](test_button_README.md)

### 2. Widgets Input
- **AutoCompleteInput** : Champ de saisie avec autocomplétion
- **PasswordInput** : Champ de saisie de mot de passe
- **SearchInput** : Champ de recherche
- **TabReplaceTextEdit** : Éditeur de texte avec remplacement de tabulations

**Documentation :** [test_input_README.md](test_input_README.md)

### 3. Widgets Label
- **ClickableTagLabel** : Label cliquable avec comportement de tag
- **FramedLabel** : Label avec cadre
- **HoverLabel** : Label avec effets au survol
- **IndicatorLabel** : Label indicateur de statut

**Documentation :** [test_label_README.md](test_label_README.md)

### 4. Widgets Misc
- **CircularTimer** : Timer circulaire animé
- **OptionSelector** : Sélecteur d'options avec animation
- **ToggleIcon** : Icône toggleable
- **ToggleSwitch** : Interrupteur toggle moderne

**Documentation :** [test_misc_README.md](test_misc_README.md)

## Statistiques Globales

| Catégorie | Widgets | Tests | Couverture |
|-----------|---------|-------|------------|
| Button | 3 | 35 | 100% |
| Input | 4 | 48 | 100% |
| Label | 4 | 36 | 100% |
| Misc | 4 | 46 | 100% |
| **Total** | **15** | **165** | **100%** |

## Exécution des Tests

### Tous les tests unitaires
```bash
python -m pytest tests/unit/ -v
```

### Par catégorie
```bash
# Tests Button
python -m pytest tests/unit/test_button/ -v

# Tests Input
python -m pytest tests/unit/test_input/ -v

# Tests Label
python -m pytest tests/unit/test_label/ -v

# Tests Misc
python -m pytest tests/unit/test_misc/ -v
```

### Par widget spécifique
```bash
# Exemple pour DateButton
python -m pytest tests/unit/test_button/test_date_button.py -v

# Exemple pour AutoCompleteInput
python -m pytest tests/unit/test_input/test_auto_complete_input.py -v
```

### Utilisation du script de test
```bash
# Tous les tests unitaires
python tests/run_tests.py --type unit

# Tests avec couverture
python tests/run_tests.py --type unit --coverage
```

## Fixtures Disponibles

### Fixtures Qt
- `qt_application` : Instance QApplication pour les tests Qt
- `qt_widget_cleanup` : Nettoyage automatique des widgets Qt

### Fixtures Personnalisées
- `wait_for_signal` : Attendre l'émission d'un signal Qt

## Bonnes Pratiques

### 1. Structure des Tests
- Un fichier de test par widget
- Nommage cohérent : `test_<widget_name>.py`
- Classes de test avec nommage descriptif

### 2. Organisation des Tests
- Tests de création (défaut et personnalisé)
- Tests des propriétés (getters/setters)
- Tests des méthodes publiques
- Tests des signaux
- Tests des événements (si applicable)

### 3. Évitement des Problèmes
- Pas de simulation d'événements Qt complexes
- Utilisation des fixtures appropriées
- Tests isolés et indépendants
- Validation des valeurs par défaut

### 4. Documentation
- Docstrings descriptives pour chaque test
- Documentation séparée par catégorie
- Exemples d'utilisation dans la documentation

## Corrections et Améliorations

### Corrections Majeures Apportées
1. **Signatures de constructeurs** : Adaptation aux APIs réelles
2. **Noms de méthodes** : Correction des noms de méthodes publiques
3. **Propriétés** : Utilisation des propriétés correctes
4. **Signaux** : Test des signaux réels émis par les widgets
5. **Valeurs par défaut** : Correction des valeurs par défaut attendues

### Améliorations Continues
- Ajout de nouveaux widgets au fur et à mesure
- Amélioration de la couverture de test
- Optimisation des performances des tests
- Documentation mise à jour régulièrement

## Support

Pour toute question ou problème avec les tests :
1. Consulter la documentation spécifique de la catégorie
2. Vérifier les exemples d'utilisation
3. Examiner les tests existants pour référence
4. Suivre les bonnes pratiques établies 