"""
guidelineDialog
===============================================================================
"""
from wbDefcon import Color

from .guidelineDialogUI import GuidelineDialogUI

class GuidelineDialog(GuidelineDialogUI):

    def __init__(self, parent, guidelineDict=None):
        super().__init__(parent)
        self.textCtrl_name.Hint = "None"
        self.dialogButtonsOK.SetDefault()
        if guidelineDict is None:
            guidelineDict = {}
        self.textCtrl_name.Value = guidelineDict.get("name", "")
        self.spinCtrl_x.Value = round(guidelineDict.get("x", 0))
        self.spinCtrl_y.Value = round(guidelineDict.get("y", 0))
        self.spinCtrlDouble_angle.Value = guidelineDict.get("angle", 0.0)
        color = guidelineDict.get("color")
        if color:
            self.checkBox_color.Value = True
            self.colourPicker.SetColour(color.wx)
        else:
            self.checkBox_color.Value = False

    @property
    def guidelineDict(self):
        result = dict(
            name=self.textCtrl_name.Value,
            x=self.spinCtrl_x.Value,
            y=self.spinCtrl_y.Value,
            angle=self.spinCtrlDouble_angle.Value,
            # color=None,
        )
        if self.colourPicker.IsEnabled():
            result["color"] = Color.from_wx(self.colourPicker.GetColour())
        return result

    def on_update_colourPicker(self, event):
        event.Enable(self.checkBox_color.Value)
