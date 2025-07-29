# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

"""
Configuration pytest pour les tests unitaires d'EzQt_Widgets.
"""

import pytest
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer


@pytest.fixture(scope="session")
def qt_application():
    """
    Fixture pour créer une instance QApplication pour tous les tests.
    Nécessaire pour tester les widgets Qt.
    """
    # ////// CRÉER L'APPLICATION QT
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    yield app

    # ////// NETTOYAGE APRÈS LES TESTS
    app.quit()


@pytest.fixture
def qt_widget_cleanup(qt_application):
    """
    Fixture pour nettoyer les widgets après chaque test.
    """
    yield qt_application

    # ////// FORCER LE NETTOYAGE DES WIDGETS
    qt_application.processEvents()


@pytest.fixture
def wait_for_signal(qt_application):
    """
    Fixture pour attendre qu'un signal soit émis.
    """

    def _wait_for_signal(signal, timeout=1000):
        """Attendre qu'un signal soit émis avec un timeout."""
        timer = QTimer()
        timer.setSingleShot(True)
        timer.start(timeout)

        # ////// CONNECTER LE SIGNAL À UN SLOT QUI ARRÊTE LE TIMER
        def stop_timer():
            timer.stop()

        signal.connect(stop_timer)

        # ////// ATTENDRE QUE LE TIMER S'ARRÊTE
        while timer.isActive():
            qt_application.processEvents()

        return not timer.isActive()

    return _wait_for_signal


@pytest.fixture
def mock_icon_path(tmp_path):
    """
    Fixture pour créer un chemin d'icône temporaire.
    """
    icon_file = tmp_path / "test_icon.png"
    # ////// CRÉER UN FICHIER D'ICÔNE TEMPORAIRE SIMPLE
    with open(icon_file, "wb") as f:
        # ////// EN-TÊTE PNG MINIMAL
        f.write(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf5\xc7\xd3\xf7\x00\x00\x00\x00IEND\xaeB`\x82"
        )

    return str(icon_file)


@pytest.fixture
def mock_svg_path(tmp_path):
    """
    Fixture pour créer un fichier SVG temporaire.
    """
    svg_file = tmp_path / "test_icon.svg"
    # ////// CRÉER UN FICHIER SVG TEMPORAIRE SIMPLE
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="16" height="16" xmlns="http://www.w3.org/2000/svg">
    <rect width="16" height="16" fill="red"/>
</svg>"""

    with open(svg_file, "w", encoding="utf-8") as f:
        f.write(svg_content)

    return str(svg_file)
