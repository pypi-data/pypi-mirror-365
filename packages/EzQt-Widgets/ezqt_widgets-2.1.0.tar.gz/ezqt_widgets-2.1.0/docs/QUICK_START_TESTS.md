# 🚀 Guide de démarrage rapide - Tests EzQt_Widgets

## ✅ Vérification rapide

Pour vérifier que tout fonctionne :

```bash
python run_tests.py --type unit
```

## 🧪 Exécution des tests

### **Méthode 1 : Script personnalisé (recommandé)**

```bash
# Tests unitaires
python run_tests.py --type unit

# Tests avec couverture
python run_tests.py --coverage

# Mode verbeux
python run_tests.py --verbose

# Exclure les tests lents
python run_tests.py --fast
```

### **Méthode 2 : Pytest direct**

```bash
# Tests simples
python -m pytest tests/test_simple.py -v

# Tests unitaires
python -m pytest tests/unit/ -v

# Tests spécifiques
python -m pytest tests/unit/test_button/test_icon_button.py -v

# Avec couverture
python -m pytest --cov=ezqt_widgets --cov-report=html
```

## 📊 Résultats attendus

### **Tests unitaires réussis :**
```
============================= test session starts =============================
collected 17 items

tests/unit/test_button/test_icon_button.py::TestColorizePixmap::test_colorize_pixmap_basic PASSED
tests/unit/test_button/test_icon_button.py::TestColorizePixmap::test_colorize_pixmap_transparent PASSED
...
===================================== 16 passed, 1 skipped in 2.34s ======================================
```

### **Tests unitaires :**
```
============================= test session starts =============================
collected 17 items

tests/unit/test_button/test_icon_button.py::TestColorizePixmap::test_colorize_pixmap_basic PASSED
tests/unit/test_button/test_icon_button.py::TestColorizePixmap::test_colorize_pixmap_transparent PASSED
...
===================================== 17 passed in 5.23s ======================================
```

## 🔧 Dépannage

### **Erreur "QGuiApplication before QPixmap"**
- ✅ **Résolu** : Les fixtures Qt sont configurées dans `conftest.py`

### **Erreur d'import**
```bash
pip install -e .
```

### **Erreur de dépendances**
```bash
pip install pytest pytest-qt pytest-cov
```

### **Tests qui s'arrêtent**
- Vérifiez que PySide6 est installé
- Consultez les logs pytest pour plus de détails

## 📁 Structure des tests

```
tests/
├── run_tests.py                # Run des tests
├── conftest.py                 # Configuration pytest
├── unit/                       # Tests unitaires
│   └── test_button/
│       └── test_icon_button.py # Tests IconButton
└── README.md                   # Documentation complète
```

## 🎯 Prochaines étapes

1. **Ajouter des tests** pour les autres widgets
2. **Créer des tests d'intégration**
3. **Configurer l'intégration continue**
4. **Améliorer la couverture de code**

## 📞 Support

Si vous rencontrez des problèmes :
1. Exécutez `python run_tests.py --type unit`
2. Vérifiez les dépendances
3. Consultez `tests/README.md` pour plus de détails 