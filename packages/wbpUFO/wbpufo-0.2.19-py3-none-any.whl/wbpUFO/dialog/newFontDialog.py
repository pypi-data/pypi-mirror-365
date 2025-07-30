"""
newFontDialog
===============================================================================
"""
import wx

from .newFontDialogUI import NewFontDialogUI


class NewFontDialog(NewFontDialogUI):
    @property
    def familyName(self):
        return self.textCtrl_family.Value

    @property
    def styleName(self):
        return self.textCtrl_style.Value

    @property
    def unitsPerEm(self):
        return self.spinCtrl_upm.Value
