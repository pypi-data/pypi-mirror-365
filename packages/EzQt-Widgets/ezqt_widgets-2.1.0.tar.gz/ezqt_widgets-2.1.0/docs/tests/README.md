# Tests Unitaires - EzQt_Widgets

## 📋 Vue d'ensemble

Ce répertoire contient tous les tests unitaires pour le projet EzQt_Widgets. Les tests sont organisés de manière modulaire pour correspondre à la structure du code source.

## 🏗️ Structure

```
tests/
├── conftest.py                    # Configuration pytest et fixtures
├── unit/                          # Tests unitaires
│   ├── test_button/               # Tests des widgets bouton
│   ├── test_input/                # Tests des widgets input
│   ├── test_label/                # Tests des widgets label
│   └── test_misc/                 # Tests des widgets divers
└── integration/                   # Tests d'intégration (optionnel)
```

## 🚀 Exécution des tests

### Installation des dépendances

```bash
pip install -e ".[dev]"
```

### Lancement rapide

```bash
# Tous les tests
python run_tests.py

# Tests unitaires uniquement
python run_tests.py --type unit

# Tests avec couverture
python run_tests.py --coverage

# Mode verbeux
python run_tests.py --verbose

# Exclure les tests lents
python run_tests.py --fast
```

### Avec pytest directement

```bash
# Tests unitaires
pytest -m unit

# Tests d'intégration
pytest -m integration

# Avec couverture
pytest --cov=ezqt_widgets --cov-report=html

# Tests spécifiques
pytest tests/unit/test_button/test_icon_button.py
```

## 🧪 Types de tests

### Tests unitaires (`@pytest.mark.unit`)

- **Objectif** : Tester chaque composant individuellement
- **Portée** : Fonctions, classes, méthodes
- **Isolation** : Utilisation de mocks et fixtures
- **Vitesse** : Rapides (< 1 seconde par test)

### Tests d'intégration (`@pytest.mark.integration`)

- **Objectif** : Tester l'interaction entre composants
- **Portée** : Widgets dans une interface
- **Isolation** : Interface Qt complète
- **Vitesse** : Plus lents (1-5 secondes par test)

### Tests lents (`@pytest.mark.slow`)

- **Objectif** : Tests nécessitant du temps (réseau, fichiers)
- **Exclusion** : `pytest -m "not slow"`

## 🔧 Fixtures disponibles

### `qt_application`
Instance QApplication partagée pour tous les tests.

### `qt_widget_cleanup`
Nettoie automatiquement les widgets après chaque test.

### `wait_for_signal`
Attend qu'un signal Qt soit émis avec timeout.

### `mock_icon_path`
Chemin vers un fichier d'icône temporaire.

### `mock_svg_path`
Chemin vers un fichier SVG temporaire.

## 📊 Couverture de code

La couverture est générée automatiquement avec :
- Rapport terminal : `--cov-report=term-missing`
- Rapport HTML : `--cov-report=html:htmlcov`
- Rapport XML : `--cov-report=xml`

## 🎯 Bonnes pratiques

### 1. Nommage des tests
```python
def test_widget_creation_default():
    """Test de création avec paramètres par défaut."""
    pass

def test_widget_property_setter():
    """Test du setter de propriété."""
    pass
```

### 2. Organisation des classes de test
```python
class TestWidgetName:
    """Tests pour la classe WidgetName."""
    
    def test_method_name_scenario(self):
        """Test de la méthode dans un scénario spécifique."""
        pass
```

### 3. Utilisation des fixtures
```python
def test_widget_creation(self, qt_widget_cleanup, mock_icon_path):
    """Test avec fixtures."""
    widget = Widget(icon=mock_icon_path)
    assert widget.icon is not None
```

### 4. Tests de signaux
```python
def test_signal_emission(self, qt_widget_cleanup, wait_for_signal):
    """Test d'émission de signal."""
    widget = Widget()
    assert wait_for_signal(widget.someSignal)
```

## 🐛 Débogage

### Mode debug
```bash
pytest --pdb
```

### Affichage des prints
```bash
pytest -s
```

### Tests spécifiques
```bash
pytest -k "test_icon_button"
```

## 📈 Métriques

- **Couverture cible** : > 90%
- **Temps d'exécution** : < 30 secondes pour tous les tests
- **Fiabilité** : 0% de tests flaky

## 🔄 Intégration continue

Les tests sont automatiquement exécutés :
- À chaque commit
- Avant chaque merge
- Avant chaque release

## 📝 Ajout de nouveaux tests

1. Créer le fichier de test dans le bon répertoire
2. Suivre la convention de nommage
3. Utiliser les fixtures appropriées
4. Ajouter les marqueurs nécessaires
5. Vérifier la couverture

## 🚨 Problèmes courants

### QApplication déjà créée
```python
# Utiliser la fixture qt_application
def test_widget(app):
    pass
```

### Tests qui échouent aléatoirement
- Ajouter des délais avec `QTimer`
- Utiliser `wait_for_signal`
- Vérifier l'isolation des tests

### Mémoire qui fuit
- Utiliser `qt_widget_cleanup`
- Supprimer explicitement les widgets
- Vérifier les connexions de signaux 