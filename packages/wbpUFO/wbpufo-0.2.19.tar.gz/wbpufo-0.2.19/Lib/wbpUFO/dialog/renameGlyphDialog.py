"""
renameGlyphDialog
===============================================================================

Rename Glyph Dialog and some Validators
"""
import string
import re

import wx
from fontTools.agl import AGL2UV, UV2AGL

from .renameGlyphDialogUI import RenameGlyphDialogUI

uni4name = re.compile(r"uni[0-9A-F]{4}")
uni5name = re.compile(r"(u|uni)[0-9A-F]{5}")

class BaseRenameValidator(wx.Validator):
    """
    Base class for all Validators in RenameGlyphDialog
    """
    validChars = ""

    def __init__(self):
        super().__init__()
        self.Bind(wx.EVT_CHAR, self.OnChar)

    @property
    def dialog(self):
        return self.Window.Parent

    def Clone(self):
        return self.__class__()

    def OnChar(self, event):
        key = event.GetKeyCode()
        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return
        if chr(key) in self.validChars:
            event.Skip()
            return
        if not wx.Validator.IsSilent():
            wx.Bell()
        return


class GlyphNameValidator(BaseRenameValidator):
    """
    Glyph name validator.
    Used in textCtrlNameNew of RenameGlyphDialog
    """
    validChars = string.ascii_letters + string.digits + ".:+-_|~*"

    def TransferToWindow(self):
        self.Window.Value = self.dialog.glyph.name
        return True

    def TransferFromWindow(self):
        self.dialog.glyphname = self.Window.Value
        return True

    def Validate(self, parent):
        glyphname = self.Window.Value
        if not glyphname:
            wx.LogError("Glyph name must not be empty.")
            return False
        if glyphname[0] in string.digits:
            wx.LogError("Glyph name must not start with a digit.")
            return False
        return True


class UnicodesValidator(BaseRenameValidator):
    """
    Unicode validator.
    Used in textCtrlUniNew of RenameGlyphDialog
    """
    validChars = string.hexdigits + " "

    def TransferToWindow(self):
        self.Window.Value = " ".join([f"{u:04X}" for u in self.dialog.glyph.unicodes])
        return True

    def TransferFromWindow(self):
        value = self.Window.Value
        if value:
            self.dialog.unicodes = [int(s, 16) for s in self.Window.Value.split()]
        else:
            self.dialog.unicodes = []
        return True

    def Validate(self, parent):
        value = self.Window.Value
        if not value:
            return True
        try:
            unis = [int(s, 16) for s in self.Window.Value.split()]
            for uni in unis:
                if not (0x0 <= uni <= 0xFFFFF):
                    wx.LogError(f"Invalid unicode: {uni:04X}")
                    return False
            return True
        except ValueError:
            wx.LogError("Can't convert Unicodes to sequece of integers.")
            return False


class RenameGlyphDialog(RenameGlyphDialogUI):
    """
    Implementation of the Rename Glyph Dialog
    """
    settingCache = {
        "ReplaceExisting": False,
        "KeepReplaced": True,
        "InComposites": True,
        "InKerning": True,
        "InGroups": True,
        "InFeatures": True,
        "AllLayers": True,
    }

    def __init__(self, parent, glyph):
        super().__init__(parent)
        self.glyph = glyph
        self.font = glyph.font
        self.glyphname = glyph.name
        self.unicodes = glyph.unicodes
        if self.font:
            self.componentReferences = self.font.componentReferences
        else:
            self.componentReferences = None
        self.textCtrlNameCurrent.Value = glyph.name
        self.textCtrlUniCurrent.Value = " ".join(["%04X" % u for u in glyph.unicodes])
        self.textCtrlNameNew.Validator = GlyphNameValidator()
        self.textCtrlUniNew.Validator = UnicodesValidator()
        self.checkBoxReplaceExisting.Value = self.settingCache["ReplaceExisting"]
        self.checkBoxKeepReplaced.Value = self.settingCache["KeepReplaced"]
        self.checkBoxInComposites.Value = self.settingCache["InComposites"]
        self.checkBoxInKerning.Value = self.settingCache["InKerning"]
        self.checkBoxInGroups.Value = self.settingCache["InGroups"]
        self.checkBoxInFeatures.Value = self.settingCache["InFeatures"]
        self.checkBoxAllLayers.Value = self.settingCache["AllLayers"]

        self.buttonSizerOK.Bind(wx.EVT_UPDATE_UI, self.update_buttonOK )

    @property
    def replaceExisting(self):
        return self.checkBoxReplaceExisting.Enabled and self.checkBoxReplaceExisting.Value

    @property
    def keepReplaced(self):
        return self.radioBoxKeepReplaced.Enabled and self.radioBoxKeepReplaced.Selection == 0
        # return self.replaceExisting and self.checkBoxKeepReplaced.Value

    @property
    def inComposites(self):
        return self.checkBoxInComposites.Enabled and self.checkBoxInComposites.Value

    @property
    def inKerning(self):
        return self.checkBoxInKerning.Enabled and self.checkBoxInKerning.Value

    @property
    def inGroups(self):
        return self.checkBoxInGroups.Enabled and self.checkBoxInGroups.Value

    @property
    def inFeatures(self):
        return self.checkBoxInFeatures.Enabled and self.checkBoxInFeatures.Value

    @property
    def allLayers(self):
        return self.checkBoxAllLayers.Enabled and self.checkBoxAllLayers.Value

    def on_buttonAutoName(self, event):
        if self.textCtrlUniNew.Validate():
            uni = int(self.textCtrlUniNew.Value.split()[0], 16)
            if uni in UV2AGL:
                self.textCtrlNameNew.Value = UV2AGL[uni]
            elif uni <= 0xFFFF:
                self.textCtrlNameNew.Value = "uni%04X" % uni
            else:
                self.textCtrlNameNew.Value = "u%05X" % uni

    def update_buttonAutoName(self, event):
        if self.textCtrlUniNew.Value:
            event.Enable(True)
        else:
            event.Enable(False)

    def on_buttonAutoUni(self, event):
        name = self.textCtrlNameNew.Value
        if name in AGL2UV:
            self.textCtrlUniNew.Value = "%04X" % AGL2UV[name]
        elif uni5name.match(name):
            self.textCtrlUniNew.Value = name[-5:]
        elif uni4name.match(name):
            self.textCtrlUniNew.Value = name[-4:]
        else:
            self.textCtrlUniNew.Value = ""

    def update_buttonAutoUni(self, event):
        if self.textCtrlNameNew.Value:
            event.Enable(True)
        else:
            event.Enable(False)

    def update_checkBoxReplaceExisting(self, event):
        event.Enable(self.textCtrlNameNew.Value != self.glyph.name and self.textCtrlNameNew.Value in self.font)

    def update_checkBoxKeepReplaced(self, event):
        event.Enable(self.checkBoxReplaceExisting.Enabled and self.checkBoxReplaceExisting.Value)

    def update_radioBoxKeepReplaced(self, event):
        event.Enable(self.checkBoxReplaceExisting.Enabled and self.checkBoxReplaceExisting.Value)

    def update_checkBoxInComposites(self, event):
        if self.componentReferences and self.glyph.name in self.componentReferences:
            event.Enable(True)
        else:
            event.Enable(False)

    def update_checkBoxInKerning(self, event):
        if self.font and self.font.kerning:
            event.Enable(True)
        else:
            event.Enable(False)

    def update_checkBoxInGroups(self, event):
        if self.font and self.font.groups:
            event.Enable(True)
        else:
            event.Enable(False)

    def update_checkBoxInFeatures(self, event):
        if self.font and self.font.features.text:
            event.Enable(True)
        else:
            event.Enable(False)

    def on_buttonOK(self, event):
        self.settingCache["ReplaceExisting"] = self.checkBoxReplaceExisting.Value
        self.settingCache["KeepReplaced"] = self.radioBoxKeepReplaced.Selection == 0
        self.settingCache["InComposites"] = self.checkBoxInComposites.Value
        self.settingCache["InKerning"] = self.checkBoxInKerning.Value
        self.settingCache["InGroups"] = self.checkBoxInGroups.Value
        self.settingCache["InFeatures"] = self.checkBoxInFeatures.Value
        event.Skip()

    def update_buttonOK(self, event):
        if self.checkBoxReplaceExisting.Enabled and not self.replaceExisting:
            event.Enable(False)
        else:
            event.Enable(True)
