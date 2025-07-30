"""
layerDialog
===============================================================================

Get name and color for a layer
"""
import wx

from wbDefcon import Color

from .layerDialogUI import LayerDialogUI


class LayerDialog(LayerDialogUI):
    def __init__(self, name=None, color=None):
        super().__init__(wx.GetApp().TopWindow)
        self.textCtrl_name.Hint = "<New Layer>"
        if isinstance(name, str):
            self.textCtrl_name.Value = name
        if isinstance(color, Color):
            self.colourPicker.Colour = color.wx
        self.sizer_buttonOK.SetDefault()
        self.sizer_buttonOK.Bind(wx.EVT_UPDATE_UI, self.onUpdate_ButtonOK)

    @property
    def layer_name(self):
        return self.textCtrl_name.Value.strip()

    @property
    def layer_color(self):
        if self.colourPicker.Colour == wx.WHITE:
            return None
        return Color.from_wx(self.colourPicker.Colour)

    def onUpdate_ButtonOK(self, event):
        event.Enable(bool(self.layer_name))


def getLayerInfo(name=None, color=None):
    with LayerDialog(name, color) as layerDialog:
        if layerDialog.ShowModal() == wx.ID_OK:
            return layerDialog.layer_name, layerDialog.layer_color
    return None, None
