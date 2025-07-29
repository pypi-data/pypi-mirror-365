# Documentation de l'API - EzQt Widgets

## Vue d'ensemble

Ce dossier contient la documentation complète de l'API de tous les widgets de la bibliothèque EzQt. Chaque fichier présente un aspect spécifique des widgets avec leurs fonctionnalités, paramètres, propriétés et exemples d'utilisation.

## Structure de la Documentation de l'API

### 📋 Documentation Générale
- **[WIDGETS_DOCUMENTATION.md](WIDGETS_DOCUMENTATION.md)** - Vue d'ensemble complète de tous les widgets
  - Description de tous les widgets disponibles
  - Comparaison des fonctionnalités
  - Guide d'utilisation général
  - Exemples d'intégration

### 🎛️ Documentation par Module

#### Widgets de Boutons
- **[BUTTONS_DOCUMENTATION.md](BUTTONS_DOCUMENTATION.md)** - Widgets de boutons spécialisés
  - **DateButton** : Bouton de sélection de date avec calendrier intégré
  - **IconButton** : Bouton avec support d'icône et texte optionnel
  - **LoaderButton** : Bouton avec animation de chargement intégrée

#### Widgets d'Entrée
- **[INPUTS_DOCUMENTATION.md](INPUTS_DOCUMENTATION.md)** - Widgets d'entrée avancés
  - **AutoCompleteInput** : Champ de texte avec autocomplétion
  - **PasswordInput** : Champ de mot de passe avec indicateur de force
  - **SearchInput** : Champ de recherche avec historique
  - **TabReplaceTextEdit** : Éditeur de texte avec remplacement de tabulations

#### Widgets de Labels
- **[LABELS_DOCUMENTATION.md](LABELS_DOCUMENTATION.md)** - Widgets de labels interactifs
  - **ClickableTagLabel** : Tag cliquable avec état basculable
  - **FramedLabel** : Label encadré pour le style avancé
  - **HoverLabel** : Label avec icône au survol
  - **IndicatorLabel** : Indicateur de statut avec LED colorée

#### Widgets Divers
- **[MISC_DOCUMENTATION.md](MISC_DOCUMENTATION.md)** - Widgets divers et utilitaires
  - **CircularTimer** : Timer circulaire animé
  - **OptionSelector** : Sélecteur d'options avec animation
  - **ToggleIcon** : Icône basculable ouvert/fermé
  - **ToggleSwitch** : Commutateur moderne avec animation

#### Guide de Style
- **[STYLE_GUIDE.md](STYLE_GUIDE.md)** - Guide de style et bonnes pratiques
  - **Conventions de code** : Standards de codage
  - **Bonnes pratiques** : Recommandations d'utilisation
  - **Styles QSS** : Personnalisation des apparences
  - **Accessibilité** : Principes d'accessibilité

## Organisation du Contenu

### Pour Chaque Widget, la Documentation Inclut :

#### 📝 Description et Fonctionnalités
- **Description générale** du widget et de son rôle
- **Liste des fonctionnalités** principales
- **Cas d'usage** typiques
- **Avantages** par rapport aux widgets Qt standard

#### ⚙️ Paramètres et Configuration
- **Paramètres du constructeur** avec types et valeurs par défaut
- **Options de configuration** disponibles
- **Exemples de configuration** courantes

#### 🔧 Propriétés et Méthodes
- **Propriétés** accessibles en lecture/écriture
- **Méthodes utilitaires** disponibles
- **Fonctions d'aide** intégrées
- **Exemples d'utilisation** des propriétés

#### 📡 Signaux et Événements
- **Signaux émis** par le widget
- **Types de données** des signaux
- **Exemples de connexion** des signaux
- **Gestion des événements** utilisateur

#### 💡 Exemples d'Utilisation
- **Exemples de base** pour démarrer rapidement
- **Exemples avancés** pour des cas d'usage complexes
- **Intégration** avec d'autres widgets
- **Styles personnalisés** avec QSS

#### 🛠️ Fonctions Utilitaires
- **Fonctions d'aide** associées au module
- **Utilitaires de conversion** et de formatage
- **Fonctions de validation** et de traitement
- **Outils de développement** et de debug

## Navigation et Utilisation

### 🔍 Comment Naviguer
1. **Commencez par** `WIDGETS_DOCUMENTATION.md` pour une vue d'ensemble
2. **Consultez** la documentation spécifique au module qui vous intéresse
3. **Utilisez** les exemples d'utilisation pour comprendre l'implémentation
4. **Référez-vous** aux fonctions utilitaires pour des tâches spécifiques
5. **Consultez** `STYLE_GUIDE.md` pour les bonnes pratiques

### 📚 Ordre de Lecture Recommandé
1. **Débutants** : `WIDGETS_DOCUMENTATION.md` → Module spécifique → Exemples
2. **Utilisateurs expérimentés** : Module spécifique → Fonctions utilitaires → Intégration
3. **Développeurs** : Toute la documentation → Exemples avancés → Styles personnalisés
4. **Mainteneurs** : `STYLE_GUIDE.md` → Standards de code → Bonnes pratiques

### 🎯 Recherche Rapide
- **Ctrl+F** dans chaque fichier pour rechercher des termes spécifiques
- **Table des matières** en début de chaque fichier pour navigation rapide
- **Exemples de code** pour copier-coller et adapter

## Contribution à la Documentation

### 📝 Amélioration de la Documentation
- **Ajout d'exemples** : Complétez les exemples d'utilisation
- **Correction d'erreurs** : Signalez et corrigez les erreurs
- **Nouvelles fonctionnalités** : Documentez les nouvelles fonctionnalités
- **Traduction** : Améliorez la traduction française

### 🔄 Mise à Jour
- **Synchronisation** avec le code source
- **Nouveaux widgets** : Ajout de documentation pour les nouveaux widgets
- **Changements d'API** : Mise à jour des paramètres et propriétés
- **Exemples** : Ajout d'exemples pour les nouveaux cas d'usage

## Liens Utiles

### 📖 Documentation Générale
- **[../README.md](../README.md)** - Guide principal de la documentation

### 🧪 Tests et Exemples
- **[../tests/](../tests/)** - Documentation des tests
- **[../tests/QUICK_START_TESTS.md](../tests/QUICK_START_TESTS.md)** - Guide de démarrage des tests

### 🔗 Ressources Externes
- **Code source** : `../../ezqt_widgets/` - Implémentation des widgets
- **Tests** : `../../tests/` - Tests unitaires et d'intégration
- **Exemples** : `../../examples/` - Exemples d'utilisation complets

---

**Documentation de l'API EzQt Widgets** - Guide complet pour l'utilisation et l'intégration des widgets spécialisés. 