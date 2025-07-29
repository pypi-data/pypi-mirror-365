# 📚 Documentation - EzQt_Widgets

## 📋 **Vue d'ensemble**

Ce dossier contient toute la documentation du projet EzQt_Widgets, organisée par catégorie pour faciliter la navigation.

## 📖 **Documentation Générale**

### **Guide de Style**
- [**STYLE_GUIDE.md**](./STYLE_GUIDE.md) - Guide de style et conventions de code
- [**CHANGELOG.md**](./CHANGELOG.md) - Historique des versions et changements

## 🧪 **Documentation des Tests**

### **Guides de Test**
- [**QUICK_START_TESTS.md**](./QUICK_START_TESTS.md) - Guide rapide pour démarrer les tests
- [**tests/README.md**](./tests/README.md) - Documentation complète des tests
- [**tests/unit_README.md**](./tests/unit_README.md) - Tests unitaires détaillés

### **Tests par Catégorie**
- [**tests/test_button_README.md**](./tests/test_button_README.md) - Tests des widgets bouton
- [**tests/test_label_README.md**](./tests/test_label_README.md) - Tests des widgets label
- [**tests/test_input_README.md**](./tests/test_input_README.md) - Tests des widgets input

## 🚀 **Utilisation**

### **Exécution des Tests**
```bash
# Depuis la racine du projet
python tests/run_tests.py --type unit

# Ou directement
python -m pytest tests/unit/ -v
```

### **Navigation**
- **README principal** : [../README.md](../README.md)
- **Code source** : [../ezqt_widgets/](../ezqt_widgets/)
- **Tests** : [../tests/](../tests/)

## 📊 **Statistiques**

### **Tests Disponibles**
- **Widgets Bouton** : 59 tests (55 passent, 4 skipped)
- **Widgets Label** : 70 tests (67 passent, 3 skipped)
- **Widgets Input** : 112 tests ✅
- **Total** : 244 tests (234 passent, 7 skipped)

### **Couverture Estimée**
- **IconButton** : 90%
- **DateButton** : ~30%
- **LoaderButton** : ~27%
- **ClickableTagLabel** : ~40%
- **FramedLabel** : ~35%
- **HoverLabel** : ~30%
- **IndicatorLabel** : ~40%

---

**État global :** 🟢 **OPÉRATIONNEL** (234/244 tests passent, 7 skipped) 