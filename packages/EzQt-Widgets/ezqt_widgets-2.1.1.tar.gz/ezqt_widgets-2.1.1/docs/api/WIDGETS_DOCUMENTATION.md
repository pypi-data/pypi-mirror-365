# Documentation Technique des Widgets EzQt

## Vue d'ensemble

Cette documentation présente tous les widgets disponibles dans la bibliothèque EzQt, organisés par modules fonctionnels. Chaque widget est documenté avec ses fonctionnalités, paramètres, propriétés et signaux.

## Table des matières

1. [Widgets de Boutons](#widgets-de-boutons)
2. [Widgets d'Entrée](#widgets-dentrée)
3. [Widgets de Labels](#widgets-de-labels)
4. [Widgets Divers](#widgets-divers)

---

## Widgets de Boutons

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

---

## Widgets d'Entrée

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

---

## Widgets de Labels

### ClickableTagLabel

**Fichier :** `ezqt_widgets/label/clickable_tag_label.py`

**Description :** Label cliquable de type tag avec état basculable.

**Fonctionnalités :**
- Tag cliquable avec état activé/désactivé
- Émet des signaux lors du clic et du changement d'état
- Texte, police, largeur/hauteur minimale personnalisables
- Couleur de statut personnalisable (nom traditionnel ou hex)
- Compatible QSS (propriétés type/class/status)
- Calcul automatique de la taille minimale
- Focus clavier et accessibilité

**Paramètres :**
- `name` : str, optionnel - Texte à afficher dans le tag (défaut : "")
- `enabled` : bool, optionnel - État initial (défaut : False)
- `status_color` : str, optionnel - Couleur quand sélectionné (défaut : "#0078d4")
- `min_width` : int, optionnel - Largeur minimale (défaut : None, calculé automatiquement)
- `min_height` : int, optionnel - Hauteur minimale (défaut : None, calculé automatiquement)
- `parent` : QWidget, optionnel - Widget parent (défaut : None)

**Propriétés :**
- `name` : str - Obtenir ou définir le texte du tag
- `enabled` : bool - Obtenir ou définir l'état activé
- `status_color` : str - Obtenir ou définir la couleur de statut
- `min_width` : int - Obtenir ou définir la largeur minimale
- `min_height` : int - Obtenir ou définir la hauteur minimale

**Signaux :**
- `clicked()` - Émis quand le tag est cliqué
- `toggle_keyword(str)` - Émis avec le nom du tag lors du basculement
- `stateChanged(bool)` - Émis quand l'état activé change

---

### FramedLabel

**Fichier :** `ezqt_widgets/label/framed_label.py`

**Description :** Label flexible basé sur QFrame, conçu pour le style et la mise en page avancés dans les applications Qt.

**Fonctionnalités :**
- Accès basé sur les propriétés au texte du label (text) et à l'alignement (alignment)
- Émet un signal textChanged(str) quand le texte change
- Permet l'injection de feuille de style personnalisée pour l'apparence avancée
- Adapté pour une utilisation comme en-tête, label de section, ou tout contexte où un label stylé est nécessaire

**Paramètres :**
- `text` : str, optionnel - Le texte initial à afficher dans le label (défaut : "")
- `parent` : QWidget, optionnel - Widget parent (défaut : None)
- `alignment` : Qt.AlignmentFlag, optionnel - L'alignement du texte du label (défaut : Qt.AlignmentFlag.AlignCenter)
- `style_sheet` : str, optionnel - Feuille de style personnalisée à appliquer au QFrame (défaut : None, utilise un arrière-plan transparent)
- `min_width` : int, optionnel - Contrainte de largeur minimale pour le widget (défaut : None)
- `min_height` : int, optionnel - Contrainte de hauteur minimale pour le widget (défaut : None)

**Propriétés :**
- `text` : str - Obtenir ou définir le texte du label
- `alignment` : Qt.AlignmentFlag - Obtenir ou définir l'alignement du label
- `min_width` : int - Obtenir ou définir la contrainte de largeur minimale
- `min_height` : int - Obtenir ou définir la contrainte de hauteur minimale

**Signaux :**
- `textChanged(str)` - Émis quand le texte du label change

---

### HoverLabel

**Fichier :** `ezqt_widgets/label/hover_label.py`

**Description :** QLabel interactif qui affiche une icône flottante au survol et émet un signal quand l'icône est cliquée.

**Fonctionnalités :**
- Affiche une icône personnalisée au survol, avec opacité, taille, superposition de couleur et remplissage configurables
- Émet un signal hoverIconClicked quand l'icône est cliquée
- Gère les événements de souris et les changements de curseur pour une meilleure UX
- Le texte et l'icône peuvent être définis à la construction ou via les propriétés
- L'icône peut être activée/désactivée dynamiquement
- Supporte les icônes PNG/JPG et SVG (local, ressource, URL)
- Gestion robuste des erreurs de chargement d'icônes

**Paramètres :**
- `parent` : QWidget, optionnel - Widget parent (défaut : None)
- `icon` : QIcon ou str, optionnel - L'icône à afficher au survol (QIcon, chemin, ressource, URL, ou SVG)
- `text` : str, optionnel - Le texte du label (défaut : "")
- `opacity` : float, optionnel - L'opacité de l'icône de survol (défaut : 0.5)
- `icon_size` : QSize ou tuple, optionnel - La taille de l'icône de survol (défaut : QSize(16, 16))
- `icon_color` : QColor ou str, optionnel - Superposition de couleur optionnelle à appliquer à l'icône (défaut : None)
- `icon_padding` : int, optionnel - Remplissage (en px) à droite du texte pour l'icône (défaut : 8)
- `icon_enabled` : bool, optionnel - Si l'icône est affichée au survol (défaut : True)
- `min_width` : int, optionnel - Largeur minimale du widget (défaut : None)

**Propriétés :**
- `opacity` : float - Obtenir ou définir l'opacité de l'icône de survol
- `hover_icon` : QIcon - Obtenir ou définir l'icône affichée au survol
- `icon_size` : QSize - Obtenir ou définir la taille de l'icône de survol
- `icon_color` : QColor ou str ou None - Obtenir ou définir la superposition de couleur de l'icône de survol
- `icon_padding` : int - Obtenir ou définir le remplissage droit pour l'icône
- `icon_enabled` : bool - Activer ou désactiver l'icône de survol

**Signaux :**
- `hoverIconClicked()` - Émis quand l'icône de survol est cliquée

**Méthodes utilitaires :**
- `clear_icon()` - Efface l'icône

---

### IndicatorLabel

**Fichier :** `ezqt_widgets/label/indicator_label.py`

**Description :** Widget d'indicateur de statut dynamique basé sur QFrame, conçu pour afficher un label de statut et une LED colorée dans les applications Qt.

**Fonctionnalités :**
- États dynamiques définis via un dictionnaire configurable (status_map) (texte, état, couleur)
- Accès basé sur les propriétés au statut actuel (status)
- Émet un signal statusChanged(str) quand le statut change
- Permet des ensembles de statuts et couleurs personnalisés pour divers cas d'usage
- Adapté pour les indicateurs en ligne/hors ligne, statut de service, etc.

**Paramètres :**
- `parent` : QWidget, optionnel - Widget parent (défaut : None)
- `status_map` : dict, optionnel - Dictionnaire définissant les états possibles. Chaque clé est un nom d'état, et chaque valeur est un dict avec les clés :
  - text (str) : Le label à afficher
  - state (str) : La valeur définie comme propriété Qt pour le style
  - color (str) : La couleur de la LED (toute couleur CSS valide)
- `initial_status` : str, optionnel - La clé de statut initiale à utiliser (défaut : "neutral")

**Propriétés :**
- `status` : str - Obtenir ou définir la clé de statut actuelle

**Signaux :**
- `statusChanged(str)` - Émis quand le statut change

**Méthodes utilitaires :**
- `set_status(status)` - Définit le statut

---

## Widgets Divers

### CircularTimer

**Fichier :** `ezqt_widgets/misc/circular_timer.py`

**Description :** Timer circulaire animé pour indiquer une progression ou un temps écoulé.

**Fonctionnalités :**
- Animation circulaire de progression
- Couleurs personnalisables pour l'arc et le centre
- Modes d'épaisseur d'arc configurables
- Boucle automatique optionnelle
- Signaux pour les événements de cycle

**Paramètres :**
- `parent` : QWidget, optionnel - Parent Qt (défaut : None)
- `duration` : int, optionnel - Durée totale de l'animation en millisecondes (défaut : 5000)
- `ring_color` : QColor | str, optionnel - Couleur de l'arc de progression (défaut : #0078d4)
- `node_color` : QColor | str, optionnel - Couleur du centre (défaut : #2d2d2d)
- `ring_width_mode` : str, optionnel - "small", "medium" (défaut), ou "large"
- `pen_width` : int | float, optionnel - Épaisseur de l'arc (prioritaire sur ring_width_mode si défini)
- `loop` : bool, optionnel - Si True, le timer boucle automatiquement à chaque cycle (défaut : False)

**Propriétés :**
- `duration` : int - Durée totale de l'animation
- `elapsed` : int - Temps écoulé depuis le début de l'animation
- `running` : bool - Indique si le timer est en cours d'animation
- `ring_color` : QColor - Couleur de l'arc de progression
- `node_color` : QColor - Couleur du centre
- `ring_width_mode` : str - "small", "medium", "large"
- `pen_width` : float - Épaisseur de l'arc (prioritaire sur ring_width_mode)
- `loop` : bool - Si True, le timer boucle automatiquement à chaque cycle

**Signaux :**
- `timerReset()` - Émis lorsque le timer est réinitialisé
- `clicked()` - Émis lors d'un clic sur le widget
- `cycleCompleted()` - Émis à chaque fin de cycle (même si loop=False)

**Méthodes utilitaires :**
- `startTimer()` - Démarre le timer
- `stopTimer()` - Arrête le timer
- `resetTimer()` - Réinitialise le timer

---

### OptionSelector

**Fichier :** `ezqt_widgets/misc/option_selector.py`

**Description :** Widget de sélection d'options avec sélecteur animé.

**Fonctionnalités :**
- Plusieurs options sélectionnables affichées comme des labels
- Sélecteur animé qui se déplace entre les options
- Mode de sélection unique (comportement radio)
- Sélection par défaut configurable par ID (index)
- Animations fluides avec courbes d'accélération
- Événements de clic pour la sélection d'options
- Utilise des IDs en interne pour une gestion robuste des valeurs

**Paramètres :**
- `items` : List[str] - Liste des textes d'options à afficher
- `default_id` : int, optionnel - ID d'option sélectionnée par défaut (index) (défaut : 0)
- `min_width` : int, optionnel - Contrainte de largeur minimale pour le widget (défaut : None)
- `min_height` : int, optionnel - Contrainte de hauteur minimale pour le widget (défaut : None)
- `orientation` : str, optionnel - Orientation de mise en page : "horizontal" ou "vertical" (défaut : "horizontal")
- `animation_duration` : int, optionnel - Durée de l'animation du sélecteur en millisecondes (défaut : 300)
- `parent` : QWidget, optionnel - Widget parent (défaut : None)

**Propriétés :**
- `value` : str - Obtenir ou définir l'option actuellement sélectionnée
- `value_id` : int - Obtenir ou définir l'ID de l'option actuellement sélectionnée
- `options` : List[str] - Obtenir la liste des options disponibles
- `default_id` : int - Obtenir ou définir l'ID de l'option par défaut
- `selected_option` : FramedLabel - Obtenir le widget d'option actuellement sélectionné
- `orientation` : str - Obtenir ou définir l'orientation de mise en page ("horizontal" ou "vertical")
- `min_width` : int - Obtenir ou définir la contrainte de largeur minimale
- `min_height` : int - Obtenir ou définir la contrainte de hauteur minimale
- `animation_duration` : int - Obtenir ou définir la duré d'animation en millisecondes

**Signaux :**
- `clicked()` - Émis quand une option est cliquée
- `valueChanged(str)` - Émis quand la valeur sélectionnée change
- `valueIdChanged(int)` - Émis quand l'ID de valeur sélectionnée change

**Méthodes utilitaires :**
- `initialize_selector(default_id)` - Initialise le sélecteur
- `add_option(option_id, option_text)` - Ajoute une option
- `toggle_selection(option_id)` - Bascule la sélection d'une option

---

### ToggleIcon

**Fichier :** `ezqt_widgets/misc/toggle_icon.py`

**Description :** Label avec icônes basculables pour indiquer un état ouvert/fermé.

**Fonctionnalités :**
- Icônes pour les états ouvert et fermé
- Basculement d'état au clic
- Couleurs personnalisables
- Support de différentes sources d'icônes

**Paramètres :**
- `parent` : QWidget, optionnel - Parent Qt (défaut : None)
- `opened_icon` : str | QIcon | QPixmap, optionnel - Icône à afficher quand l'état est "opened"
- `closed_icon` : str | QIcon | QPixmap, optionnel - Icône à afficher quand l'état est "closed"
- `icon_size` : int, optionnel - Taille des icônes en pixels (défaut : 16)
- `icon_color` : QColor | str, optionnel - Couleur à appliquer aux icônes (défaut : blanc avec 0.5 opacité)
- `initial_state` : str, optionnel - État initial ("opened" ou "closed", défaut : "closed")
- `min_width` : int, optionnel - Largeur minimale du widget
- `min_height` : int, optionnel - Hauteur minimale du widget

**Propriétés :**
- `state` : str - État actuel ("opened" ou "closed")
- `opened_icon` : QPixmap - Icône de l'état ouvert
- `closed_icon` : QPixmap - Icône de l'état fermé
- `icon_size` : int - Taille des icônes
- `icon_color` : QColor - Couleur des icônes
- `min_width` : int - Largeur minimale
- `min_height` : int - Hauteur minimale

**Signaux :**
- `stateChanged(str)` - Émis quand l'état change ("opened" ou "closed")
- `clicked()` - Émis lors d'un clic sur le widget

**Méthodes utilitaires :**
- `toggle_state()` - Bascule l'état
- `set_state_opened()` - Définit l'état ouvert
- `set_state_closed()` - Définit l'état fermé
- `is_opened()` - Vérifie si l'état est ouvert
- `is_closed()` - Vérifie si l'état est fermé

---

### ToggleSwitch

**Fichier :** `ezqt_widgets/misc/toggle_switch.py`

**Description :** Widget de commutateur moderne avec cercle glissant animé.

**Fonctionnalités :**
- Animation fluide lors du basculement
- Couleurs personnalisables pour les états activé/désactivé
- Taille et rayon de bordure configurables
- Fonctionnalité de basculement au clic
- Accès basé sur les propriétés à l'état
- Signal émis lors du changement d'état

**Paramètres :**
- `parent` : QWidget, optionnel - Widget parent (défaut : None)
- `checked` : bool, optionnel - État initial du commutateur (défaut : False)
- `width` : int, optionnel - Largeur du commutateur (défaut : 50)
- `height` : int, optionnel - Hauteur du commutateur (défaut : 24)
- `animation` : bool, optionnel - Animer le basculement (défaut : True)

**Propriétés :**
- `checked` : bool - Obtenir ou définir l'état du commutateur
- `width` : int - Obtenir ou définir la largeur du commutateur
- `height` : int - Obtenir ou définir la hauteur du commutateur
- `animation` : bool - Obtenir ou définir si l'animation est activée

**Signaux :**
- `toggled(bool)` - Émis quand l'état du commutateur change

**Méthodes utilitaires :**
- `toggle()` - Bascule l'état du commutateur

---

## Utilisation Générale

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

### Exemple d'Utilisation

```python
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
from ezqt_widgets.button import DateButton, IconButton
from ezqt_widgets.input import PasswordInput
from ezqt_widgets.misc import ToggleSwitch

app = QApplication([])
window = QWidget()
layout = QVBoxLayout()

# Création d'un bouton de date
date_button = DateButton(placeholder="Sélectionner une date")
layout.addWidget(date_button)

# Création d'un bouton avec icône
icon_button = IconButton(text="Mon Bouton", icon="path/to/icon.png")
layout.addWidget(icon_button)

# Création d'un champ de mot de passe
password_input = PasswordInput()
layout.addWidget(password_input)

# Création d'un commutateur
toggle = ToggleSwitch(checked=True)
layout.addWidget(toggle)

window.setLayout(layout)
window.show()
app.exec()
```

### Personnalisation des Styles

Tous les widgets supportent la personnalisation via QSS (Qt Style Sheets) :

```python
# Exemple de style personnalisé
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

### Gestion des Signaux

```python
# Connexion des signaux
date_button.dateChanged.connect(lambda date: print(f"Date sélectionnée: {date}"))
password_input.strengthChanged.connect(lambda strength: print(f"Force: {strength}"))
toggle.toggled.connect(lambda checked: print(f"Commutateur: {checked}"))
```

Cette documentation couvre tous les widgets disponibles dans la bibliothèque EzQt avec leurs fonctionnalités, paramètres, propriétés et signaux respectifs. 