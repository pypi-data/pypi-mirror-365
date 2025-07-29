# 🏷️ Tests des Widgets Label - EzQt_Widgets

## 📋 **Vue d'ensemble**

Cette section documente les tests unitaires pour les widgets **Label** d'EzQt_Widgets. Ces widgets fournissent des composants d'affichage interactifs et spécialisés.

## 🧪 **Widgets Testés**

### 1. **ClickableTagLabel** (15 tests)
Widget de label cliquable avec comportement de toggle et états visuels.

**Tests couverts :**
- ✅ Création avec paramètres par défaut et personnalisés
- ✅ Propriétés (name, enabled, status_color, min_width, min_height)
- ✅ Signaux (`clicked`, `toggle_keyword`, `stateChanged`)
- ✅ Événements souris et clavier
- ✅ Comportement de toggle (clic et espace)
- ✅ Accessibilité et focus
- ✅ Validation des propriétés
- ✅ Instances multiples

### 2. **FramedLabel** (15 tests)
Widget de label avec cadre personnalisable et options d'alignement.

**Tests couverts :**
- ✅ Création avec paramètres par défaut et personnalisés
- ✅ Propriétés (text, alignment, stylesheet, min_width, min_height)
- ✅ Signal (`textChanged`)
- ✅ Options d'alignement (left, center, right, top, bottom)
- ✅ Gestion du texte (vide, long, caractères spéciaux)
- ✅ Stylesheet personnalisé
- ✅ Dimensions minimales
- ✅ Propriété type pour QSS
- ✅ Instances multiples

### 3. **HoverLabel** (20 tests)
Widget de label avec effets de survol et gestion d'icônes.

**Tests couverts :**
- ✅ Création avec paramètres par défaut et personnalisés
- ✅ Propriétés (text, hover_icon, icon_opacity, icon_size, icon_color, icon_padding, icon_enabled)
- ✅ Signal (`hoverIconClicked`)
- ✅ Événements souris (move, press, enter, leave)
- ✅ Événements de peinture et redimensionnement
- ✅ Gestion des icônes (QIcon, fichier, SVG)
- ✅ Méthode `clear_icon`
- ✅ Changements de curseur
- ✅ Instances multiples

### 4. **IndicatorLabel** (18 tests)
Widget de label avec indicateurs de statut et transitions.

**Tests couverts :**
- ✅ Création avec paramètres par défaut et personnalisés
- ✅ Propriétés (text, status, status_map, min_width, min_height)
- ✅ Signal (`statusChanged`)
- ✅ Méthode `set_status`
- ✅ Carte de statuts par défaut et personnalisée
- ✅ Transitions de statut
- ✅ Propriété type pour QSS
- ✅ Instances multiples
- ✅ Gestion des statuts invalides

## 📊 **Statistiques des Tests**

| Widget | Tests | Pass | Skip | Fail | Couverture |
|--------|-------|------|------|------|------------|
| **ClickableTagLabel** | 15 | 15 | 0 | 0 | ~40% |
| **FramedLabel** | 15 | 15 | 0 | 0 | ~35% |
| **HoverLabel** | 20 | 20 | 0 | 0 | ~30% |
| **IndicatorLabel** | 18 | 18 | 0 | 0 | ~40% |
| **Total Label** | **68** | **68** | **0** | **0** | **~36%** |

## 🎯 **Fonctionnalités Testées**

### **Propriétés des Widgets**
- Getters et setters
- Validation des valeurs
- Changements dynamiques
- Valeurs par défaut
- Dimensions minimales

### **Gestion des Événements**
- Tests évités pour les événements Qt problématiques
- Focus sur les méthodes et propriétés
- Intégration avec les signaux Qt

### **Qt Signals**
- **ClickableTagLabel** : `clicked`, `toggle_keyword`, `stateChanged`
- **FramedLabel** : `textChanged`
- **HoverLabel** : `hoverIconClicked`
- **IndicatorLabel** : `statusChanged`

### **Gestion des Données**
- **ClickableTagLabel** : États et toggle behavior
- **FramedLabel** : Texte et alignement
- **HoverLabel** : Icônes et effets de survol
- **IndicatorLabel** : Statuts et transitions

### **Intégration Qt**
- **QLabel** : Héritage et fonctionnalités de base
- **QIcon** : Gestion d'icônes
- **QMouseEvent** : Événements souris
- **QKeyEvent** : Événements clavier

## 🚀 **Exécution des Tests**

### **Tous les tests Label**
```bash
python tests/run_tests.py --type unit --category label
python -m pytest tests/unit/test_label/ -v
```

### **Tests par widget**
```bash
# ClickableTagLabel
python -m pytest tests/unit/test_label/test_clickable_tag_label.py -v

# FramedLabel
python -m pytest tests/unit/test_label/test_framed_label.py -v

# HoverLabel
python -m pytest tests/unit/test_label/test_hover_label.py -v

# IndicatorLabel
python -m pytest tests/unit/test_label/test_indicator_label.py -v
```

### **Tests avec couverture**
```bash
python -m pytest tests/unit/test_label/ --cov=ezqt_widgets.label --cov-report=html
```

## 🔧 **Configuration des Tests**

### **Fixtures Utilisées**
- `qt_widget_cleanup` : Nettoyage automatique des widgets Qt
- `mock_icon_path` : Chemin d'icône temporaire
- `mock_svg_path` : Chemin SVG temporaire

### **Mocks et Patches**
- `QMouseEvent` : Pour les tests d'événements souris
- `QKeyEvent` : Pour les tests d'événements clavier
- `QEnterEvent`, `QEvent` : Pour les tests d'entrée/sortie
- `QPixmap`, `QIcon` : Pour les tests d'icônes

### **Cas de Test Spéciaux**
- **Événements** : Souris, clavier, focus
- **Icônes** : QIcon, fichiers, SVG
- **Texte** : Caractères spéciaux, Unicode
- **Cas limites** : Valeurs vides, extrêmes, invalides

## 📝 **Notes Importantes**

### **Tests Évités**
- Tests d'événements Qt complexes (mousePressEvent, keyPressEvent, etc.)
- Tests d'interactions utilisateur avancées
- Tests de rendu graphique complexe

### **Tests Alternatifs**
- Tests directs des propriétés et méthodes
- Tests des signaux via connexions
- Tests de validation et de robustesse
- Tests des fonctions utilitaires

### **Couverture**
- **Widgets principaux** : Couverture variable (30-40%)
- **Intégration Qt** : Tests des fonctionnalités essentielles
- **Signaux** : Tests complets des signaux émis

## 🔄 **Maintenance**

### **Ajout de Nouveaux Tests**
1. Créer le fichier de test dans `tests/unit/test_label/`
2. Suivre la convention de nommage `test_<widget_name>.py`
3. Utiliser les fixtures appropriées
4. Documenter les nouveaux tests dans ce README

### **Mise à Jour des Statistiques**
Après chaque modification des tests, mettre à jour :
- Le nombre de tests par widget
- Les statistiques de couverture
- La liste des fonctionnalités testées

## 🐛 **Problèmes Connus**

### **Aucun problème connu actuellement**
- Tous les tests passent ✅
- Fixtures Qt fonctionnelles ✅
- Mocks appropriés en place ✅

---

**Dernière mise à jour :** 2025-01-19  
**Version des tests :** 1.0.0  
**Statut :** 🟢 **OPÉRATIONNEL** (68/68 tests passent) 