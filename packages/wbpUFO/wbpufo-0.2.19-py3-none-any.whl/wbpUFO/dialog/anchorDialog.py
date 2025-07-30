"""
anchorDialog
===============================================================================
"""
import wx

from wbDefcon import Color

from .anchorDialogUI import AnchorDialogUI


class AnchorDialog(AnchorDialogUI):
    def __init__(self, parent, anchorDict=None):
        super().__init__(parent)
        self.textCtrl_name.Hint = "None"
        self.dialogButtonsOK.SetDefault()
        if anchorDict is None:
            anchorDict = {}
        self.textCtrl_name.Value = anchorDict.get("name", "")
        self.spinCtrl_x.Value = round(anchorDict.get("x", 0))
        self.spinCtrl_y.Value = round(anchorDict.get("y", 0))
        color = anchorDict.get("color")
        if color:
            self.checkBox_color.Value = True
            self.colourPicker.SetColour(color.wx)
        else:
            self.checkBox_color.Value = False

    @property
    def anchorDict(self):
        result = dict(
            x=self.spinCtrl_x.Value,
            y=self.spinCtrl_y.Value,
            name=self.textCtrl_name.Value,
            color=None,
        )
        if self.colourPicker.IsEnabled():
            result["color"] = Color.from_wx(self.colourPicker.GetColour())
        return result

    def on_update_colourPicker(self, event):
        event.Enable(self.checkBox_color.Value)
