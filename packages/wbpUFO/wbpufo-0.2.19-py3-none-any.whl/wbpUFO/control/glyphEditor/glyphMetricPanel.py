from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from weakref import ReferenceType, ref

import wx

from .glyphMetricPanelUI import GlyphMetricPanelUI

if TYPE_CHECKING:
    from wbDefcon import Component, Glyph

    from .editPanel import GlyphEditPanel


class GlyphMetricPanel(GlyphMetricPanelUI):
    refreshNotifications = (
        "Glyph.WidthChanged",
        "Glyph.LeftMarginDidChange",
        "Glyph.RightMarginDidChange",
        "Glyph.ContoursChanged",
        "Glyph.ComponentsChanged",
        "Glyph.ComponentBaseGlyphDataChanged",
    )

    def __init__(
        self,
        parent: GlyphEditPanel,
        id: int = wx.ID_ANY,
        pos: wx.Position = wx.DefaultPosition,
        size: wx.Size = wx.DefaultSize,
        style: int = wx.BORDER_NONE | wx.TAB_TRAVERSAL,
        name: str = "GlyphMetricPanel",
    ):
        self._glyph: Optional[ReferenceType[Glyph]] = None
        super().__init__(parent, id=id, pos=pos, size=size, style=style, name=name)

    @property
    def glyph(self) -> Optional[Glyph]:
        if self._glyph is None:
            return None
        return self._glyph()

    @glyph.setter
    def glyph(self, value: Glyph):
        if self.glyph == value:
            return
        del self.glyph
        self._glyph = ref(value)
        self._beginObsservation()
        self._setControlValues()
        self.Refresh()

    @glyph.deleter
    def glyph(self):
        if self._glyph is None:
            return
        self._endObservation()
        self._glyph = None
        self.Refresh()

    def _setControlValues(self):
        if self._glyph is None:
            return
        glyph = self.glyph
        try:
            if glyph.leftMargin is not None:
                self.spinCtrlDouble_LSB.Value = glyph.leftMargin
            self.spinCtrlDouble_width.Value = glyph.width
            if glyph.rightMargin is not None:
                self.spinCtrlDouble_RSB.Value = glyph.rightMargin
        except RuntimeError:
            self._endObservation()

    # ------------------------
    # Notification Observation
    # ------------------------

    def _beginObsservation(self) -> None:
        glyph = self.glyph
        for notificationName in self.refreshNotifications:
            if not glyph.hasObserver(self, notificationName):
                glyph.addObserver(self, "handleNotification", notificationName)

    def _endObservation(self) -> None:
        glyph = self.glyph
        for notificationName in self.refreshNotifications:
            if glyph.hasObserver(self, notificationName):
                glyph.removeObserver(self, notificationName)

    def handleNotification(self, notification):
        self._setControlValues()

    # event handlers

    def on_spinCtrlDouble_LSB(self, event: wx.SpinDoubleEvent):
        glyph = self.glyph
        dx = event.Value - glyph.leftMargin
        if not dx:
            return
        glyph.moveBy((dx, 0))
        font = glyph.font
        for glyphName in font.componentReferences.get(glyph.name, ()):
            if glyphName in font:
                compositeGlyph: Glyph = glyph.font[glyphName]
                component: Component
                for component in compositeGlyph.components:
                    if component.baseGlyph == glyph.name:
                        component.moveBy((-dx, 0))

    def onUpdate_spinCtrlDouble_LSB(self, event: wx.UpdateUIEvent):
        glyph = self.glyph
        if glyph is None or glyph.leftMargin is None:
            self.spinCtrlDouble_LSB.Value = 0
            event.Enable(False)
            return
        event.Enable(True)

    def on_spinCtrlDouble_width(self, event: wx.SpinDoubleEvent):
        self.glyph.width = event.Value

    def onUpdate_spinCtrlDouble_width(self, event: wx.UpdateUIEvent):
        if self.glyph is None:
            self.spinCtrlDouble_width.Value = 0
            event.Enable(False)
            return
        event.Enable(True)

    def on_spinCtrlDouble_RSB(self, event: wx.SpinDoubleEvent):
        self.glyph.rightMargin = event.Value

    def onUpdate_spinCtrlDouble_RSB(self, event: wx.UpdateUIEvent):
        glyph = self.glyph
        if glyph is None or glyph.rightMargin is None:
            self.spinCtrlDouble_RSB.Value = 0
            event.Enable(False)
            return
        event.Enable(True)

    def Destroy(self):
        del self.glyph
        return super().Destroy()
