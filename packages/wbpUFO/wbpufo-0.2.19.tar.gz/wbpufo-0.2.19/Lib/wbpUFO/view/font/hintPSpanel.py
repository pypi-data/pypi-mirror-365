"""
hintPSpanel
===============================================================================

"""
import logging
from string import digits

import wx

from .stemPanelUI import StemPanelUI
from .zonePanelUI import ZonePanelUI

log = logging.getLogger(__name__)


class NumberValidator(wx.Validator):
    def __init__(self):
        super().__init__()
        self._validChars = digits + ".+-"
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return NumberValidator()

    def Validate(self, win):
        ctrl = self.GetWindow()
        if not ctrl.Enabled:
            return True
        value = ctrl.GetValue()
        for c in value:
            if c not in self._validChars:
                return False
        return True

    def OnChar(self, event):
        key = event.GetKeyCode()
        log.debug("key: %r, chr: %r", key, chr(key))

        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if chr(key) in self._validChars:
            event.Skip()
            return

        if not wx.Validator.IsSilent():
            wx.Bell()
        return

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True


class ZonePanel(ZonePanelUI):
    def __init__(
        self,
        parent: wx.Window,
        id: int = wx.ID_ANY,
        pos: wx.Point = wx.DefaultPosition,
        size: wx.Size = wx.DefaultSize,
        style:int=wx.BORDER_NONE | wx.TAB_TRAVERSAL,
        name: str = wx.EmptyString,
    ):
        ZonePanelUI.__init__(
            self, parent, id=id, pos=pos, size=size, style=style, name=name
        )
        self._value = []
        self._maxValueLen = 0
        self._newZone = False
        self.textCtrl_bottom.Validator = NumberValidator()
        self.textCtrl_top.Validator = NumberValidator()

    def GetValue(self):
        return self._value

    def SetValue(self, value):
        if value == self._value:
            return
        if isinstance(value, (list, tuple)) and len(value) % 2 == 0:
            self._value = value
            self.listCtrl_zone.SetItemCount(int(len(value) / 2))
            self.listCtrl_zone.Refresh()
            self.Validator.TransferFromWindow()

    Value = property(GetValue, SetValue)

    def on_listCtrl_zone_selected(self, event):
        self.textCtrl_bottom.Value = str(self.Value[event.Index * 2])
        self.textCtrl_top.Value = str(self.Value[event.Index * 2 + 1])
        self._newZone = False

    def onUpdate_editControls(self, event):
        do_edit = self._newZone or self.listCtrl_zone.SelectedItemCount > 0
        if do_edit:
            event.Enable(True)
        else:
            self.textCtrl_bottom.Value = ""
            self.textCtrl_top.Value = ""
            event.Enable(False)

    def on_button_apply(self, event):
        try:
            bottom = int(self.textCtrl_bottom.Value)
        except ValueError:
            try:
                bottom = float(self.textCtrl_bottom.Value)
            except ValueError:
                wx.LogWarning(
                    f"Invalid value for bottom edge of zone\n\nCan't convert '{self.textCtrl_bottom.Value}' to number."
                )
                self.textCtrl_bottom.SelectAll()
                self.textCtrl_bottom.SetFocus()
                return
        try:
            top = int(self.textCtrl_top.Value)
        except ValueError:
            try:
                top = float(self.textCtrl_top.Value)
            except ValueError:
                wx.LogWarning(
                    f"Invalid value for top edge of zone\n\nCan't convert '{self.textCtrl_top.Value}' to number."
                )
                self.textCtrl_top.SelectAll()
                self.textCtrl_top.SetFocus()
                return
        zones = self.Value[:]
        if not self._newZone:
            idx = self.listCtrl_zone.FocusedItem
            del zones[idx * 2 : idx * 2 + 2]
        zones.extend([bottom, top])
        zones.sort()
        self.Value = zones
        # self.Validator.TransferFromWindow()
        self._newZone = False
        # event.Skip()

    def on_button_add(self, event):
        self._newZone = True
        self.textCtrl_bottom.Value = "0"
        self.textCtrl_top.Value = "0"

    def onUpdate_button_add(self, event):
        event.Enable(len(self._value) < self._maxValueLen)

    def on_button_remove(self, event):
        zones = self.Value[:]
        idx = self.listCtrl_zone.FocusedItem
        del zones[idx * 2 : idx * 2 + 2]
        self.Value = zones

    def onUpdate_button_remove(self, event):
        event.Enable(self.listCtrl_zone.SelectedItemCount > 0)


class StemPanel(StemPanelUI):
    def __init__(
        self,
        parent: wx.Window,
        id: int = wx.ID_ANY,
        pos: wx.Point = wx.DefaultPosition,
        size: wx.Size = wx.DefaultSize,
        style:int=wx.BORDER_NONE | wx.TAB_TRAVERSAL,
        name: str = wx.EmptyString,
    ):
        StemPanelUI.__init__(
            self, parent, id=id, pos=pos, size=size, style=style, name=name
        )
        self._value = []
        self._maxValueLen = 12
        self._newStem = False
        self.textCtrl_width.Validator = NumberValidator()

    def GetValue(self):
        return self._value

    def SetValue(self, value):
        if value == self._value:
            return
        if isinstance(value, (list, tuple)):
            self._value = value
            self.listCtrl_stem.SetItemCount(len(value))
            self.listCtrl_stem.Refresh()
            self.Validator.TransferFromWindow()

    Value = property(GetValue, SetValue)

    def on_listCtrl_stem_selected(self, event):
        self.textCtrl_width.Value = str(self.Value[event.Index])
        self._newStem = False

    def onUpdate_editControls(self, event):
        do_edit = self._newStem or self.listCtrl_stem.SelectedItemCount > 0
        if do_edit:
            event.Enable(True)
        else:
            self.textCtrl_width.Value = ""
            event.Enable(False)

    def on_button_apply(self, event):
        try:
            width = int(self.textCtrl_width.Value)
        except ValueError:
            try:
                width = float(self.textCtrl_width.Value)
            except ValueError:
                wx.LogWarning(
                    f"Invalid value for width of stem\n\nCan't convert '{self.textCtrl_width.Value}' to number."
                )
                self.textCtrl_width.SelectAll()
                self.textCtrl_width.SetFocus()
                return
        stems = self.Value[:]
        if not self._newStem:
            idx = self.listCtrl_stem.FocusedItem
            del stems[idx]
        stems.append(width)
        stems.sort()
        self.Value = stems
        self._newStem = False

    def on_button_add(self, event):
        self._newStem = True
        self.textCtrl_width.Value = "0"

    def onUpdate_button_add(self, event):
        event.Enable(len(self._value) < self._maxValueLen)

    def on_button_remove(self, event):
        stems = self.Value[:]
        idx = self.listCtrl_stem.FocusedItem
        del stems[idx]
        self.Value = stems

    def onUpdate_button_remove(self, event):
        event.Enable(self.listCtrl_stem.SelectedItemCount > 0)
