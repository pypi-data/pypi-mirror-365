import sys

import pytest

from wbDefcon.objects.component import Component
from wbDefcon.objects.font import Font

from wbpUFO.dialog.anchorDialog import AnchorDialog
from wbpUFO.dialog.applyGlyphConstructionDialog import ApplyGlyphConstructionDialog
from wbpUFO.dialog.assignLayerDialog import AssignLayerDialog
from wbpUFO.dialog.componentDialog import ComponentDialog
from wbpUFO.dialog.deleteGlyphsDialog import DeleteGlyphsDialog
from wbpUFO.dialog.findGlyphDialog import FindGlyphDialog
from wbpUFO.dialog.revertFontDialog import RevertFontDialog
from wbpUFO.dialog.selectFontsDialog import SelectFontsDialog
from wbpUFO.glyphCommand.commandListDialog import CommandListDialog

def test_AnchorDialog():
    dialog = AnchorDialog(None)
    assert isinstance(dialog, AnchorDialog)
    dialog.Destroy()


def test_ApplyGlyphConstructionDialog():
    dialog = ApplyGlyphConstructionDialog()
    assert isinstance(dialog, ApplyGlyphConstructionDialog)
    dialog.Destroy()

# todo: Fix AssignLayerDialog
# def test_AssignLayerDialog():
#     dialog = AssignLayerDialog(None)
#     assert isinstance(dialog, AssignLayerDialog)
#     dialog.Destroy()


def test_ComponentDialog():
    component = Component()
    component.baseGlyph = "A"
    dialog = ComponentDialog(None, component)
    assert isinstance(dialog, ComponentDialog)
    dialog.Destroy()


def test_DeleteGlyphsDialog():
    dialog = DeleteGlyphsDialog(0)
    assert isinstance(dialog, DeleteGlyphsDialog)
    dialog.Destroy()


def test_FindGlyphDialog():
    font = Font()
    dialog = FindGlyphDialog(None, font)
    assert isinstance(dialog, FindGlyphDialog)
    dialog.Destroy()

# todo: font needs path
# def test_RevertFontDialog():
#     font = Font()
#     font.path = "path"
#     dialog = RevertFontDialog(None, font)
#     assert isinstance(dialog, RevertFontDialog)
#     dialog.Destroy()


def test_SelectFontsDialog():
    dialog = SelectFontsDialog()
    assert isinstance(dialog, SelectFontsDialog)
    dialog.Destroy()


def test_CommandListDialog():
    dialog = CommandListDialog()
    assert isinstance(dialog, CommandListDialog)
    dialog.Destroy()


if __name__ == "__main__":
    pytest.main(sys.argv)
