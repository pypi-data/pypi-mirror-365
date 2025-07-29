# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

"""
Tests unitaires pour le widget PasswordInput (version corrigée).
"""

import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication

from ezqt_widgets.input.password_input import (
    PasswordInput,
    PasswordLineEdit,
    password_strength,
    get_strength_color,
    colorize_pixmap,
    load_icon_from_source,
)


pytestmark = pytest.mark.unit


class TestPasswordStrength:
    """Tests pour les fonctions utilitaires de force de mot de passe."""

    def test_password_strength_weak(self):
        """Test de force de mot de passe faible."""
        # ////// MOT DE PASSE TRÈS FAIBLE
        assert password_strength("") == 0
        assert password_strength("a") == 15  # 1 char + lowercase
        assert password_strength("123") == 20  # 3 chars + digits

        # ////// MOT DE PASSE FAIBLE
        assert password_strength("password") == 40  # 8+ chars + lowercase
        assert password_strength("12345678") == 45  # 8+ chars + digits

    def test_password_strength_medium(self):
        """Test de force de mot de passe moyen."""
        # ////// MOT DE PASSE MOYEN
        assert password_strength("Password") == 55  # 8+ chars + lowercase + uppercase
        assert password_strength("pass1234") == 60  # 8+ chars + lowercase + digits
        assert password_strength("PASS1234") == 60  # 8+ chars + uppercase + digits

    def test_password_strength_strong(self):
        """Test de force de mot de passe fort."""
        # ////// MOT DE PASSE FORT
        assert (
            password_strength("Password123") == 75
        )  # 8+ chars + lowercase + uppercase + digits
        assert (
            password_strength("Pass@word") == 80
        )  # 8+ chars + lowercase + uppercase + special
        assert (
            password_strength("Pass@123") == 100
        )  # 8+ chars + lowercase + uppercase + digits + special (max 100)

    def test_password_strength_very_strong(self):
        """Test de force de mot de passe très fort."""
        # ////// MOT DE PASSE TRÈS FORT
        assert password_strength("MyP@ssw0rd!") == 100  # Tous les critères
        assert password_strength("SuperS3cret#") == 100  # Tous les critères
        assert password_strength("C0mpl3x!P@ss") == 100  # Tous les critères

    def test_password_strength_edge_cases(self):
        """Test de force de mot de passe avec des cas limites."""
        # ////// CARACTÈRES SPÉCIAUX
        assert password_strength("pass@word") == 65  # 8+ chars + lowercase + special
        assert password_strength("PASS@WORD") == 65  # 8+ chars + uppercase + special

        # ////// LONGUEUR EXTREME
        assert password_strength("a" * 100) == 40  # Longueur + lowercase
        assert password_strength("A" * 100) == 40  # Longueur + uppercase

    def test_get_strength_color_weak(self):
        """Test des couleurs pour mots de passe faibles."""
        assert get_strength_color(0) == "#ff4444"  # Rouge
        assert get_strength_color(10) == "#ff4444"  # Rouge
        assert get_strength_color(29) == "#ff4444"  # Rouge

    def test_get_strength_color_medium(self):
        """Test des couleurs pour mots de passe moyens."""
        assert get_strength_color(30) == "#ffaa00"  # Orange
        assert get_strength_color(50) == "#ffaa00"  # Orange
        assert get_strength_color(59) == "#ffaa00"  # Orange

    def test_get_strength_color_good(self):
        """Test des couleurs pour mots de passe bons."""
        assert get_strength_color(60) == "#44aa44"  # Vert
        assert get_strength_color(70) == "#44aa44"  # Vert
        assert get_strength_color(79) == "#44aa44"  # Vert

    def test_get_strength_color_strong(self):
        """Test des couleurs pour mots de passe forts."""
        assert get_strength_color(80) == "#00aa00"  # Vert foncé
        assert get_strength_color(90) == "#00aa00"  # Vert foncé
        assert get_strength_color(100) == "#00aa00"  # Vert foncé


class TestColorizePixmap:
    """Tests pour la fonction colorize_pixmap."""

    def test_colorize_pixmap_basic(self, qt_widget_cleanup):
        """Test de base de colorize_pixmap."""
        # ////// CRÉER UN PIXMAP DE TEST
        original_pixmap = QPixmap(16, 16)
        original_pixmap.fill(Qt.white)

        # ////// COLORISER LE PIXMAP
        colored_pixmap = colorize_pixmap(original_pixmap, "#ff0000", 0.5)

        # ////// VÉRIFIER QUE LE RÉSULTAT EST UN PIXMAP
        assert isinstance(colored_pixmap, QPixmap)
        assert colored_pixmap.size() == original_pixmap.size()

    def test_colorize_pixmap_different_colors(self, qt_widget_cleanup):
        """Test de colorize_pixmap avec différentes couleurs."""
        original_pixmap = QPixmap(16, 16)
        original_pixmap.fill(Qt.white)

        # ////// TEST DIFFÉRENTES COULEURS
        colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff"]
        for color in colors:
            colored_pixmap = colorize_pixmap(original_pixmap, color, 0.5)
            assert isinstance(colored_pixmap, QPixmap)

    def test_colorize_pixmap_different_opacities(self, qt_widget_cleanup):
        """Test de colorize_pixmap avec différentes opacités."""
        original_pixmap = QPixmap(16, 16)
        original_pixmap.fill(Qt.white)

        # ////// TEST DIFFÉRENTES OPACITÉS
        opacities = [0.0, 0.25, 0.5, 0.75, 1.0]
        for opacity in opacities:
            colored_pixmap = colorize_pixmap(original_pixmap, "#ff0000", opacity)
            assert isinstance(colored_pixmap, QPixmap)


class TestLoadIconFromSource:
    """Tests pour la fonction load_icon_from_source."""

    def test_load_icon_from_source_none(self):
        """Test de load_icon_from_source avec None."""
        icon = load_icon_from_source(None)
        assert icon is None

    def test_load_icon_from_source_qicon(self, qt_widget_cleanup):
        """Test de load_icon_from_source avec QIcon."""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.red)
        original_icon = QIcon(pixmap)

        icon = load_icon_from_source(original_icon)
        assert isinstance(icon, QIcon)

    @patch("requests.get")
    def test_load_icon_from_source_url(self, mock_get, qt_widget_cleanup):
        """Test de load_icon_from_source avec URL."""
        # ////// MOCK LA RÉPONSE HTTP
        mock_response = MagicMock()
        mock_response.content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf5\x01\x00\x00\x00\x00IEND\xaeB`\x82"
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "image/png"}
        mock_get.return_value = mock_response

        # ////// TEST CHARGEMENT D'ICÔNE DEPUIS URL
        icon = load_icon_from_source("https://example.com/icon.png")
        assert isinstance(icon, QIcon)

    @patch("requests.get")
    def test_load_icon_from_source_url_failure(self, mock_get):
        """Test de load_icon_from_source avec échec URL."""
        # ////// MOCK L'ÉCHEC HTTP
        mock_get.side_effect = Exception("Network error")

        # ////// TEST ÉCHEC DE CHARGEMENT
        icon = load_icon_from_source("https://example.com/icon.png")
        assert icon is None


class TestPasswordLineEdit:
    """Tests pour la classe PasswordLineEdit."""

    def test_password_line_edit_creation(self, qt_widget_cleanup):
        """Test de création de PasswordLineEdit."""
        line_edit = PasswordLineEdit()

        assert line_edit is not None
        assert isinstance(line_edit, PasswordLineEdit)
        assert line_edit.echoMode() == line_edit.EchoMode.Password

    def test_password_line_edit_set_right_icon(self, qt_widget_cleanup):
        """Test de set_right_icon."""
        line_edit = PasswordLineEdit()

        # ////// CRÉER UNE ICÔNE
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.red)
        icon = QIcon(pixmap)

        # ////// DÉFINIR L'ICÔNE
        line_edit.set_right_icon(icon, QSize(20, 20))

        # ////// VÉRIFIER QUE L'ICÔNE EST DÉFINIE
        # Note: On ne peut pas facilement vérifier l'icône interne
        # mais on peut vérifier que la méthode ne lève pas d'exception
        assert line_edit is not None

    def test_password_line_edit_refresh_style(self, qt_widget_cleanup):
        """Test de refresh_style."""
        line_edit = PasswordLineEdit()

        # ////// LA MÉTHODE NE DOIT PAS LEVER D'EXCEPTION
        try:
            line_edit.refresh_style()
        except Exception as e:
            pytest.fail(f"refresh_style() a levé une exception: {e}")


class TestPasswordInput:
    """Tests pour la classe PasswordInput."""

    def test_password_input_creation_default(self, qt_widget_cleanup):
        """Test de création avec paramètres par défaut."""
        password_widget = PasswordInput()

        assert password_widget is not None
        assert isinstance(password_widget, PasswordInput)
        assert password_widget.show_strength is True
        assert password_widget.strength_bar_height == 3
        assert password_widget.show_icon is not None
        assert password_widget.hide_icon is not None
        assert password_widget.icon_size == QSize(16, 16)

    def test_password_input_creation_with_parameters(self, qt_widget_cleanup):
        """Test de création avec paramètres personnalisés."""
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.red)
        icon = QIcon(pixmap)

        password_widget = PasswordInput(
            show_strength=False,
            strength_bar_height=5,
            show_icon=icon,
            hide_icon=icon,
            icon_size=QSize(24, 24),
        )

        assert password_widget.show_strength is False
        assert password_widget.strength_bar_height == 5
        assert password_widget.show_icon is not None
        assert password_widget.hide_icon is not None
        assert password_widget.icon_size == QSize(24, 24)

    def test_password_input_properties(self, qt_widget_cleanup):
        """Test des propriétés du widget."""
        password_widget = PasswordInput()

        # ////// TEST PASSWORD PROPERTY
        password_widget.password = "test123"
        assert password_widget.password == "test123"

        # ////// TEST SHOW_STRENGTH PROPERTY
        password_widget.show_strength = False
        assert password_widget.show_strength is False

        # ////// TEST STRENGTH_BAR_HEIGHT PROPERTY
        password_widget.strength_bar_height = 10
        assert password_widget.strength_bar_height == 10

        # ////// TEST SHOW_ICON PROPERTY
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.blue)
        icon = QIcon(pixmap)
        password_widget.show_icon = icon
        assert password_widget.show_icon is not None

        # ////// TEST HIDE_ICON PROPERTY
        password_widget.hide_icon = icon
        assert password_widget.hide_icon is not None

        # ////// TEST ICON_SIZE PROPERTY
        password_widget.icon_size = QSize(32, 32)
        assert password_widget.icon_size == QSize(32, 32)

    def test_password_input_toggle_password(self, qt_widget_cleanup):
        """Test de toggle_password."""
        password_widget = PasswordInput()

        # ////// ÉTAT INITIAL (MOT DE PASSE CACHÉ)
        initial_mode = password_widget._password_input.echoMode()

        # ////// BASCULER L'AFFICHAGE
        password_widget.toggle_password()

        # ////// VÉRIFIER QUE LE MODE A CHANGÉ
        new_mode = password_widget._password_input.echoMode()
        assert new_mode != initial_mode

        # ////// BASCULER ENCORE
        password_widget.toggle_password()
        final_mode = password_widget._password_input.echoMode()
        assert final_mode == initial_mode

    def test_password_input_update_strength(self, qt_widget_cleanup):
        """Test de update_strength."""
        password_widget = PasswordInput()

        # ////// TEST MOT DE PASSE FAIBLE
        password_widget.update_strength("weak")
        # Note: On ne peut pas facilement vérifier l'état interne
        # mais on peut vérifier que la méthode ne lève pas d'exception

        # ////// TEST MOT DE PASSE FORT
        password_widget.update_strength("StrongP@ss123!")
        # La méthode ne doit pas lever d'exception

    def test_password_input_signals(self, qt_widget_cleanup):
        """Test des signaux du widget."""
        password_widget = PasswordInput()

        # ////// TEST STRENGTHCHANGED SIGNAL
        signal_received = False
        received_strength = 0

        def on_strength_changed(strength):
            nonlocal signal_received, received_strength
            signal_received = True
            received_strength = strength

        password_widget.strengthChanged.connect(on_strength_changed)

        # ////// SIMULER UN CHANGEMENT DE FORCE
        password_widget.update_strength("test123")

        # ////// VÉRIFIER QUE LE SIGNAL EST CONNECTÉ
        assert password_widget.strengthChanged is not None

        # ////// TEST ICONCLICKED SIGNAL
        icon_signal_received = False

        def on_icon_clicked():
            nonlocal icon_signal_received
            icon_signal_received = True

        password_widget.iconClicked.connect(on_icon_clicked)

        # ////// VÉRIFIER QUE LE SIGNAL EST CONNECTÉ
        assert password_widget.iconClicked is not None

    def test_password_input_refresh_style(self, qt_widget_cleanup):
        """Test de refresh_style."""
        password_widget = PasswordInput()

        # ////// LA MÉTHODE NE DOIT PAS LEVER D'EXCEPTION
        try:
            password_widget.refresh_style()
        except Exception as e:
            pytest.fail(f"refresh_style() a levé une exception: {e}")

    def test_password_input_password_validation(self, qt_widget_cleanup):
        """Test de validation des mots de passe."""
        password_widget = PasswordInput()

        # ////// TEST MOTS DE PASSE VALIDES
        valid_passwords = [
            "password",
            "Password123",
            "MyP@ssw0rd!",
            "12345678",
            "a" * 100,
        ]

        for password in valid_passwords:
            password_widget.password = password
            assert password_widget.password == password

        # ////// TEST MOT DE PASSE VIDE
        password_widget.password = ""
        assert password_widget.password == ""

    def test_password_input_icon_size_validation(self, qt_widget_cleanup):
        """Test de validation de la taille d'icône."""
        password_widget = PasswordInput()

        # ////// TEST TAILLES VALIDES
        valid_sizes = [QSize(16, 16), QSize(24, 24), QSize(32, 32)]

        for size in valid_sizes:
            password_widget.icon_size = size
            assert password_widget.icon_size == size

    def test_password_input_strength_bar_height_validation(self, qt_widget_cleanup):
        """Test de validation de la hauteur de la barre de force."""
        password_widget = PasswordInput()

        # ////// TEST HAUTEURS VALIDES
        valid_heights = [1, 3, 5, 10, 20]
        for height in valid_heights:
            password_widget.strength_bar_height = height
            assert password_widget.strength_bar_height == height

        # ////// TEST HAUTEUR ZÉRO (DEVIENT 1)
        password_widget.strength_bar_height = 0
        assert password_widget.strength_bar_height == 1

        # ////// TEST HAUTEUR NÉGATIVE (DEVIENT 1)
        password_widget.strength_bar_height = -5
        assert password_widget.strength_bar_height == 1

    def test_password_input_multiple_instances(self, qt_widget_cleanup):
        """Test avec plusieurs instances."""
        password_widget1 = PasswordInput(show_strength=True)
        password_widget2 = PasswordInput(show_strength=False)

        # ////// TEST INDÉPENDANCE DES INSTANCES
        password_widget1.password = "password1"
        password_widget2.password = "password2"

        assert password_widget1.password == "password1"
        assert password_widget2.password == "password2"
        assert password_widget1.password != password_widget2.password

    def test_password_input_dynamic_property_changes(self, qt_widget_cleanup):
        """Test des changements dynamiques de propriétés."""
        password_widget = PasswordInput()

        # ////// TEST CHANGEMENT DYNAMIQUE DE SHOW_STRENGTH
        password_widget.show_strength = False
        assert password_widget.show_strength is False

        password_widget.show_strength = True
        assert password_widget.show_strength is True

        # ////// TEST CHANGEMENT DYNAMIQUE DE STRENGTH_BAR_HEIGHT
        password_widget.strength_bar_height = 10
        assert password_widget.strength_bar_height == 10

        password_widget.strength_bar_height = 5
        assert password_widget.strength_bar_height == 5

    def test_password_input_special_characters(self, qt_widget_cleanup):
        """Test avec des caractères spéciaux dans le mot de passe."""
        password_widget = PasswordInput()

        special_passwords = [
            "pass@word",
            "user-name_123",
            "file/path/pass",
            "pass with spaces",
            "pass\nwith\nnewlines",
            "pass\twith\ttabs",
            "pass with émojis 🚀",
            "pass with unicode: 你好世界",
        ]

        for password in special_passwords:
            password_widget.password = password
            assert password_widget.password == password

    def test_password_input_large_password(self, qt_widget_cleanup):
        """Test avec un mot de passe très long."""
        password_widget = PasswordInput()

        # ////// CRÉER UN MOT DE PASSE TRÈS LONG
        long_password = "a" * 1000

        # ////// DÉFINIR LE MOT DE PASSE
        password_widget.password = long_password

        # ////// VÉRIFIER QUE LE MOT DE PASSE EST CORRECTEMENT DÉFINI
        assert password_widget.password == long_password

        # ////// VÉRIFIER QUE LA FORCE EST CALCULÉE
        password_widget.update_strength(long_password)
        # La méthode ne doit pas lever d'exception
