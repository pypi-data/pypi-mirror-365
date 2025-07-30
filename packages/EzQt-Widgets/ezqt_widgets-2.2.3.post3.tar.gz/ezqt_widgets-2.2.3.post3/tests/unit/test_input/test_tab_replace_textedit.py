# -*- coding: utf-8 -*-
# ///////////////////////////////////////////////////////////////

"""
Tests unitaires pour le widget TabReplaceTextEdit (version corrigée).
"""

import pytest
from unittest.mock import MagicMock
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from ezqt_widgets.input.tab_replace_textedit import TabReplaceTextEdit


pytestmark = pytest.mark.unit


class TestTabReplaceTextEdit:
    """Tests pour la classe TabReplaceTextEdit."""

    def test_tab_replace_textedit_creation_default(self, qt_widget_cleanup):
        """Test de création avec paramètres par défaut."""
        text_edit = TabReplaceTextEdit()

        assert text_edit is not None
        assert isinstance(text_edit, TabReplaceTextEdit)
        assert text_edit.tab_replacement == "\n"
        assert text_edit.sanitize_on_paste is True
        assert text_edit.remove_empty_lines is True
        assert text_edit.preserve_whitespace is False

    def test_tab_replace_textedit_creation_with_parameters(self, qt_widget_cleanup):
        """Test de création avec paramètres personnalisés."""
        text_edit = TabReplaceTextEdit(
            tab_replacement=" ",
            sanitize_on_paste=False,
            remove_empty_lines=False,
            preserve_whitespace=True,
        )

        assert text_edit.tab_replacement == " "
        assert text_edit.sanitize_on_paste is False
        assert text_edit.remove_empty_lines is False
        assert text_edit.preserve_whitespace is True

    def test_tab_replace_textedit_properties(self, qt_widget_cleanup):
        """Test des propriétés du widget."""
        text_edit = TabReplaceTextEdit()

        # ////// TEST TAB_REPLACEMENT PROPERTY
        text_edit.tab_replacement = "  "
        assert text_edit.tab_replacement == "  "

        # ////// TEST SANITIZE_ON_PASTE PROPERTY
        text_edit.sanitize_on_paste = False
        assert text_edit.sanitize_on_paste is False

        # ////// TEST REMOVE_EMPTY_LINES PROPERTY
        text_edit.remove_empty_lines = False
        assert text_edit.remove_empty_lines is False

        # ////// TEST PRESERVE_WHITESPACE PROPERTY
        text_edit.preserve_whitespace = True
        assert text_edit.preserve_whitespace is True

    def test_tab_replace_textedit_sanitize_text_basic(self, qt_widget_cleanup):
        """Test de la méthode sanitize_text avec des cas de base."""
        text_edit = TabReplaceTextEdit()

        # ////// TEST REMPLACEMENT DE TAB PAR DÉFAUT
        text = "col1\tcol2\tcol3"
        sanitized = text_edit.sanitize_text(text)
        assert sanitized == "col1\ncol2\ncol3"

        # ////// TEST SANS TAB
        text = "no tabs here"
        sanitized = text_edit.sanitize_text(text)
        assert sanitized == "no tabs here"

    def test_tab_replace_textedit_sanitize_text_custom_replacement(
        self, qt_widget_cleanup
    ):
        """Test de sanitize_text avec un remplacement personnalisé."""
        text_edit = TabReplaceTextEdit(tab_replacement="  ")

        # ////// TEST REMPLACEMENT PAR ESPACES
        text = "col1\tcol2\tcol3"
        sanitized = text_edit.sanitize_text(text)
        assert sanitized == "col1  col2  col3"

        # ////// TEST REMPLACEMENT PAR VIRGULE
        text_edit.tab_replacement = ","
        text = "col1\tcol2\tcol3"
        sanitized = text_edit.sanitize_text(text)
        assert sanitized == "col1,col2,col3"

    def test_tab_replace_textedit_sanitize_text_remove_empty_lines(
        self, qt_widget_cleanup
    ):
        """Test de sanitize_text avec suppression des lignes vides."""
        text_edit = TabReplaceTextEdit(remove_empty_lines=True)

        # ////// TEST AVEC LIGNES VIDES
        text = "line1\n\nline2\n\t\nline3"
        sanitized = text_edit.sanitize_text(text)
        assert sanitized == "line1\nline2\nline3"

        # ////// TEST SANS LIGNES VIDES
        text = "line1\nline2\nline3"
        sanitized = text_edit.sanitize_text(text)
        assert sanitized == "line1\nline2\nline3"

    def test_tab_replace_textedit_sanitize_text_preserve_empty_lines(
        self, qt_widget_cleanup
    ):
        """Test de sanitize_text sans suppression des lignes vides."""
        text_edit = TabReplaceTextEdit(remove_empty_lines=False)

        # ////// TEST AVEC LIGNES VIDES PRÉSERVÉES
        text = "line1\n\nline2\n\t\nline3"
        sanitized = text_edit.sanitize_text(text)
        # Les tabs deviennent des newlines par défaut, les lignes vides sont préservées
        assert sanitized == "line1\n\nline2\n\n\nline3"

    def test_tab_replace_textedit_sanitize_text_preserve_whitespace(
        self, qt_widget_cleanup
    ):
        """Test de sanitize_text avec préservation des espaces."""
        text_edit = TabReplaceTextEdit(
            preserve_whitespace=True, remove_empty_lines=True
        )

        # ////// TEST AVEC ESPACES PRÉSERVÉS
        text = "  line1  \n  line2  \n  line3  "
        sanitized = text_edit.sanitize_text(text)
        # Vérifier que les espaces sont préservés
        assert "  line1  " in sanitized
        assert "  line2  " in sanitized
        assert "  line3  " in sanitized

        # ////// TEST SANS ESPACES PRÉSERVÉS
        text_edit.preserve_whitespace = False
        sanitized = text_edit.sanitize_text(text)
        # Les espaces sont préservés mais les lignes vides supprimées
        assert sanitized == "  line1  \n  line2  \n  line3  "

    def test_tab_replace_textedit_sanitize_text_complex(self, qt_widget_cleanup):
        """Test de sanitize_text avec des cas complexes."""
        text_edit = TabReplaceTextEdit(
            tab_replacement="|", remove_empty_lines=True, preserve_whitespace=False
        )

        # ////// TEST CAS COMPLEXE
        text = (
            "  col1\t  col2  \tcol3  \n\n  col4\tcol5\t  col6  \n\t\ncol7\tcol8\tcol9"
        )
        sanitized = text_edit.sanitize_text(text)
        # Les tabs deviennent "|", les lignes vides sont supprimées
        expected = "  col1|  col2  |col3  \n  col4|col5|  col6  \n|\ncol7|col8|col9"
        assert sanitized == expected

    def test_tab_replace_textedit_sanitize_text_mixed_content(self, qt_widget_cleanup):
        """Test de sanitize_text avec du contenu mixte."""
        text_edit = TabReplaceTextEdit(tab_replacement=" -> ", remove_empty_lines=True)

        # ////// TEST CONTENU MIXTE
        text = "header1\theader2\theader3\nvalue1\tvalue2\tvalue3\n\t\t\nfooter1\tfooter2\tfooter3"
        sanitized = text_edit.sanitize_text(text)
        # Les tabs deviennent " -> ", les lignes vides sont supprimées
        expected = "header1 -> header2 -> header3\nvalue1 -> value2 -> value3\n ->  -> \nfooter1 -> footer2 -> footer3"
        assert sanitized == expected

    def test_tab_replace_textedit_sanitize_text_special_characters(
        self, qt_widget_cleanup
    ):
        """Test de sanitize_text avec des caractères spéciaux."""
        text_edit = TabReplaceTextEdit(tab_replacement="\t->\t")

        # ////// TEST CARACTÈRES SPÉCIAUX
        text = "email@domain.com\tuser-name_123\tfile/path\nspecial\tchars\there"
        sanitized = text_edit.sanitize_text(text)
        expected = "email@domain.com\t->\tuser-name_123\t->\tfile/path\nspecial\t->\tchars\t->\there"
        assert sanitized == expected

    def test_tab_replace_textedit_sanitize_text_unicode(self, qt_widget_cleanup):
        """Test de sanitize_text avec des caractères Unicode."""
        text_edit = TabReplaceTextEdit(tab_replacement=" → ")

        # ////// TEST CARACTÈRES UNICODE
        text = "你好\t世界\t测试\némojis\t🚀\t🎉\nunicode\ttext\there"
        sanitized = text_edit.sanitize_text(text)
        expected = "你好 → 世界 → 测试\némojis → 🚀 → 🎉\nunicode → text → here"
        assert sanitized == expected

    def test_tab_replace_textedit_sanitize_text_empty_string(self, qt_widget_cleanup):
        """Test de sanitize_text avec une chaîne vide."""
        text_edit = TabReplaceTextEdit()

        # ////// TEST CHAÎNE VIDE
        sanitized = text_edit.sanitize_text("")
        assert sanitized == ""

        # ////// TEST CHAÎNE AVEC SEULEMENT DES TABS
        sanitized = text_edit.sanitize_text("\t\t\t")
        # Les tabs deviennent des newlines par défaut, puis les lignes vides sont supprimées
        assert sanitized == ""

    def test_tab_replace_textedit_sanitize_text_only_tabs(self, qt_widget_cleanup):
        """Test de sanitize_text avec seulement des tabs."""
        text_edit = TabReplaceTextEdit(tab_replacement="SPACE")

        # ////// TEST SEULEMENT DES TABS
        text = "\t\t\t"
        sanitized = text_edit.sanitize_text(text)
        # Les tabs deviennent "SPACE", puis les lignes vides sont supprimées
        assert sanitized == "SPACESPACESPACE"

    def test_tab_replace_textedit_sanitize_text_multiple_tabs(self, qt_widget_cleanup):
        """Test de sanitize_text avec des tabs multiples consécutifs."""
        text_edit = TabReplaceTextEdit(tab_replacement="|")

        # ////// TEST TABS MULTIPLES
        text = "col1\t\t\tcol2"
        sanitized = text_edit.sanitize_text(text)
        assert sanitized == "col1|||col2"

    def test_tab_replace_textedit_sanitize_text_edge_cases(self, qt_widget_cleanup):
        """Test de sanitize_text avec des cas limites."""
        text_edit = TabReplaceTextEdit(tab_replacement="TAB")

        # ////// TEST TAB AU DÉBUT
        text = "\tcol1\tcol2"
        sanitized = text_edit.sanitize_text(text)
        # Les tabs deviennent "TAB"
        assert sanitized == "TABcol1TABcol2"

        # ////// TEST TAB À LA FIN
        text = "col1\tcol2\t"
        sanitized = text_edit.sanitize_text(text)
        assert sanitized == "col1TABcol2TAB"

        # ////// TEST TABS AU DÉBUT ET À LA FIN
        text = "\tcol1\tcol2\t"
        sanitized = text_edit.sanitize_text(text)
        assert sanitized == "TABcol1TABcol2TAB"

    def test_tab_replace_textedit_text_handling(self, qt_widget_cleanup):
        """Test de la gestion du texte."""
        text_edit = TabReplaceTextEdit()

        # ////// TEST SETPLAINTEXT
        text_edit.setPlainText("test text")
        assert text_edit.toPlainText() == "test text"

        # ////// TEST CLEAR
        text_edit.clear()
        assert text_edit.toPlainText() == ""

        # ////// TEST INSERTPLAINTEXT
        text_edit.insertPlainText("inserted text")
        assert text_edit.toPlainText() == "inserted text"

    def test_tab_replace_textedit_property_type(self, qt_widget_cleanup):
        """Test de la propriété type pour QSS."""
        text_edit = TabReplaceTextEdit()

        # ////// VÉRIFIER QUE LA PROPRIÉTÉ TYPE EST DÉFINIE
        assert text_edit.property("type") == "TabReplaceTextEdit"

    def test_tab_replace_textedit_refresh_style(self, qt_widget_cleanup):
        """Test de la méthode refresh_style."""
        text_edit = TabReplaceTextEdit()

        # ////// LA MÉTHODE NE DOIT PAS LEVER D'EXCEPTION
        try:
            text_edit.refresh_style()
        except Exception as e:
            pytest.fail(f"refresh_style() a levé une exception: {e}")

    def test_tab_replace_textedit_multiple_instances(self, qt_widget_cleanup):
        """Test avec plusieurs instances."""
        text_edit1 = TabReplaceTextEdit(tab_replacement="|")
        text_edit2 = TabReplaceTextEdit(tab_replacement="->")

        # ////// TEST INDÉPENDANCE DES INSTANCES
        text = "col1\tcol2\tcol3"
        sanitized1 = text_edit1.sanitize_text(text)
        sanitized2 = text_edit2.sanitize_text(text)

        assert sanitized1 == "col1|col2|col3"
        assert sanitized2 == "col1->col2->col3"

    def test_tab_replace_textedit_dynamic_property_changes(self, qt_widget_cleanup):
        """Test des changements dynamiques de propriétés."""
        text_edit = TabReplaceTextEdit()
        text = "col1\tcol2\tcol3"

        # ////// TEST CHANGEMENT DYNAMIQUE DE TAB_REPLACEMENT
        text_edit.tab_replacement = "|"
        sanitized1 = text_edit.sanitize_text(text)
        assert sanitized1 == "col1|col2|col3"

        text_edit.tab_replacement = "->"
        sanitized2 = text_edit.sanitize_text(text)
        assert sanitized2 == "col1->col2->col3"

        # ////// TEST CHANGEMENT DYNAMIQUE DE REMOVE_EMPTY_LINES
        text_with_empty = "line1\n\nline2\n\t\nline3"

        text_edit.remove_empty_lines = True
        sanitized3 = text_edit.sanitize_text(text_with_empty)
        assert sanitized3 == "line1\nline2\n->\nline3"

        text_edit.remove_empty_lines = False
        sanitized4 = text_edit.sanitize_text(text_with_empty)
        assert sanitized4 == "line1\n\nline2\n->\nline3"

    def test_tab_replace_textedit_large_text(self, qt_widget_cleanup):
        """Test avec un grand texte."""
        text_edit = TabReplaceTextEdit(tab_replacement="|")

        # ////// CRÉER UN GRAND TEXTE
        lines = []
        for i in range(1000):
            lines.append(f"col1_{i}\tcol2_{i}\tcol3_{i}")
        large_text = "\n".join(lines)

        # ////// SANITISER LE GRAND TEXTE
        sanitized = text_edit.sanitize_text(large_text)

        # ////// VÉRIFIER LE RÉSULTAT
        lines_sanitized = sanitized.split("\n")
        assert len(lines_sanitized) == 1000

        # ////// VÉRIFIER UNE LIGNE SPÉCIFIQUE
        assert "col1_0|col2_0|col3_0" in lines_sanitized[0]
        assert "col1_999|col2_999|col3_999" in lines_sanitized[999]

    def test_tab_replace_textedit_special_replacement_strings(self, qt_widget_cleanup):
        """Test avec des chaînes de remplacement spéciales."""
        text_edit = TabReplaceTextEdit()
        text = "col1\tcol2\tcol3"

        # ////// TEST CHAÎNE VIDE
        text_edit.tab_replacement = ""
        sanitized = text_edit.sanitize_text(text)
        # Chaîne vide = pas de séparation
        assert sanitized == "col1col2col3"

        # ////// TEST CHAÎNE AVEC ESPACES
        text_edit.tab_replacement = "   "
        sanitized = text_edit.sanitize_text(text)
        assert sanitized == "col1   col2   col3"

        # ////// TEST CHAÎNE AVEC CARACTÈRES SPÉCIAUX
        text_edit.tab_replacement = "\n\t"
        sanitized = text_edit.sanitize_text(text)
        assert sanitized == "col1\n\tcol2\n\tcol3"
