# Tests des Widgets Input

## 📋 **Vue d'ensemble**

Cette section documente les tests unitaires pour les widgets **Input** d'EzQt_Widgets. Ces widgets fournissent des composants d'entrée de données avancés et spécialisés.

## 🧪 **Widgets Testés**

### 1. **AutoCompleteInput** (17 tests)
Widget d'entrée avec autocomplétion basé sur QLineEdit et QCompleter.

**Tests couverts :**
- ✅ Création avec paramètres par défaut et personnalisés
- ✅ Propriétés (suggestions, case_sensitive, filter_mode, completion_mode)
- ✅ Gestion des suggestions (add, remove, clear)
- ✅ Intégration avec QCompleter
- ✅ Sensibilité à la casse
- ✅ Modes de filtrage (MatchContains, MatchStartsWith, MatchEndsWith)
- ✅ Modes de complétion (PopupCompletion, InlineCompletion, UnfilteredPopupCompletion)
- ✅ Gestion du texte et placeholder
- ✅ Suggestions multiples et caractères spéciaux
- ✅ Doublons et cas limites

### 2. **SearchInput** (20 tests)
Widget de recherche avec historique et icônes intégrées.

**Tests couverts :**
- ✅ Création avec paramètres par défaut et personnalisés
- ✅ Propriétés (search_icon, icon_position, clear_button, max_history)
- ✅ Gestion de l'historique (add, clear, set, trim)
- ✅ Gestion des icônes et positions
- ✅ Validation des paramètres
- ✅ Gestion du texte et placeholder
- ✅ Signaux (searchSubmitted)
- ✅ Historique volumineux et caractères spéciaux
- ✅ Cas limites et validation

### 3. **TabReplaceTextEdit** (25 tests)
Widget d'édition de texte avec remplacement automatique des tabulations.

**Tests couverts :**
- ✅ Création avec paramètres par défaut et personnalisés
- ✅ Propriétés (tab_replacement, sanitize_on_paste, remove_empty_lines, preserve_whitespace)
- ✅ Méthode sanitize_text avec différents cas
- ✅ Remplacement personnalisé des tabulations
- ✅ Suppression/préservation des lignes vides
- ✅ Préservation des espaces
- ✅ Cas complexes et contenu mixte
- ✅ Caractères spéciaux et Unicode
- ✅ Cas limites (chaînes vides, tabs multiples)
- ✅ Gestion du texte et propriété type
- ✅ Instances multiples et changements dynamiques
- ✅ Texte volumineux et chaînes de remplacement spéciales

### 4. **PasswordInput** (35 tests)
Widget de saisie de mot de passe avec barre de force et icônes.

**Tests couverts :**
- ✅ Création avec paramètres par défaut et personnalisés
- ✅ Propriétés (password, show_strength, strength_bar_height, show_icon, hide_icon, icon_size)
- ✅ Méthodes (toggle_password, update_strength)
- ✅ Signaux (strengthChanged, iconClicked)
- ✅ Validation des mots de passe et tailles d'icônes
- ✅ Instances multiples et changements dynamiques
- ✅ Caractères spéciaux et mots de passe volumineux

**Fonctions utilitaires testées :**
- ✅ `password_strength()` - Calcul de la force du mot de passe
- ✅ `get_strength_color()` - Couleurs selon la force
- ✅ `colorize_pixmap()` - Colorisation d'icônes
- ✅ `load_icon_from_source()` - Chargement d'icônes depuis différentes sources

**Classe PasswordLineEdit testée :**
- ✅ Création et configuration
- ✅ Gestion des icônes
- ✅ Méthodes utilitaires

## 📊 **Statistiques des Tests**

| Widget | Tests | Pass | Skip | Fail | Couverture |
|--------|-------|------|------|------|------------|
| **AutoCompleteInput** | 17 | 17 | 0 | 0 | ~85% |
| **SearchInput** | 20 | 20 | 0 | 0 | ~80% |
| **TabReplaceTextEdit** | 25 | 25 | 0 | 0 | ~90% |
| **PasswordInput** | 35 | 35 | 0 | 0 | ~85% |
| **Fonctions utilitaires** | 15 | 15 | 0 | 0 | ~95% |
| **Total Input** | **112** | **112** | **0** | **0** | **~85%** |

## 🎯 **Fonctionnalités Testées**

### **Propriétés des Widgets**
- Getters et setters
- Validation des valeurs
- Changements dynamiques
- Valeurs par défaut

### **Gestion des Événements**
- Tests évités pour les événements Qt problématiques
- Focus sur les méthodes et propriétés
- Intégration avec les signaux Qt

### **Qt Signals**
- **AutoCompleteInput** : Intégration QCompleter
- **SearchInput** : searchSubmitted
- **PasswordInput** : strengthChanged, iconClicked
- **TabReplaceTextEdit** : Pas de signaux spécifiques

### **Gestion des Données**
- **AutoCompleteInput** : Suggestions et autocomplétion
- **SearchInput** : Historique de recherche
- **TabReplaceTextEdit** : Sanitisation de texte
- **PasswordInput** : Force de mot de passe et validation

### **Intégration Qt**
- **QLineEdit** : Héritage et fonctionnalités de base
- **QCompleter** : Autocomplétion avancée
- **QPlainTextEdit** : Édition de texte riche
- **QWidget** : Composants personnalisés

## 🚀 **Exécution des Tests**

### **Tous les tests Input**
```bash
python tests/run_tests.py --type unit --category input
python -m pytest tests/unit/test_input/ -v
```

### **Tests par widget**
```bash
# AutoCompleteInput
python -m pytest tests/unit/test_input/test_auto_complete_input.py -v

# SearchInput
python -m pytest tests/unit/test_input/test_search_input.py -v

# TabReplaceTextEdit
python -m pytest tests/unit/test_input/test_tab_replace_textedit.py -v

# PasswordInput
python -m pytest tests/unit/test_input/test_password_input.py -v
```

### **Tests avec couverture**
```bash
python -m pytest tests/unit/test_input/ --cov=ezqt_widgets.input --cov-report=html
```

## 🔧 **Configuration des Tests**

### **Fixtures Utilisées**
- `qt_widget_cleanup` : Nettoyage automatique des widgets Qt
- `qt_application` : Instance QApplication pour les tests

### **Mocks et Patches**
- `requests.get` : Pour les tests de chargement d'icônes depuis URL
- `MagicMock` : Pour simuler les réponses HTTP

### **Cas de Test Spéciaux**
- **Caractères spéciaux** : Unicode, émojis, caractères spéciaux
- **Données volumineuses** : Tests de performance avec de grandes quantités
- **Cas limites** : Valeurs vides, extrêmes, invalides
- **Validation** : Tests de robustesse et d'erreurs

## 📝 **Notes Importantes**

### **Tests Évités**
- Tests d'événements Qt (mousePressEvent, keyPressEvent, etc.)
- Tests d'interactions utilisateur complexes
- Tests de rendu graphique avancé

### **Tests Alternatifs**
- Tests directs des propriétés et méthodes
- Tests des signaux via connexions
- Tests de validation et de robustesse
- Tests des fonctions utilitaires

### **Couverture**
- **Fonctions utilitaires** : Couverture complète (95%)
- **Widgets principaux** : Couverture élevée (80-90%)
- **Intégration Qt** : Tests des fonctionnalités essentielles

## 🔄 **Maintenance**

### **Ajout de Nouveaux Tests**
1. Créer le fichier de test dans `tests/unit/test_input/`
2. Suivre la convention de nommage `test_<widget_name>.py`
3. Utiliser les fixtures appropriées
4. Documenter les nouveaux tests dans ce README

### **Mise à Jour des Statistiques**
Après chaque modification des tests, mettre à jour :
- Le nombre de tests par widget
- Les statistiques de couverture
- La liste des fonctionnalités testées

---

**Dernière mise à jour :** 2025-01-19  
**Version des tests :** 1.0.0  
**Statut :** ✅ Tous les tests passent 