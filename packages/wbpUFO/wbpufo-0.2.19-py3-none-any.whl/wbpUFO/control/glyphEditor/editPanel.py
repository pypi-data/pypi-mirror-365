"""
editPanel
===============================================================================
"""
from __future__ import annotations
import logging
import wx

from wbBase.tools import get_wxBrush, get_wxFont, get_wxPen

from .canvas import Canvas
from .glyphMetricPanel import GlyphMetricPanel

log = logging.getLogger(__name__)

ID = wx.ID_ANY
pos = wx.DefaultPosition
size = wx.DefaultSize


class Ruler(wx.Panel):
    Parent: GlyphEditPanel

    def __init__(
        self,
        parent: GlyphEditPanel,
        style=wx.NO_BORDER | wx.TAB_TRAVERSAL,
        name="Ruler",
    ):
        super().__init__(parent, ID, pos, size, style, name)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetForegroundColour(wx.Colour(80, 80, 80))
        self.SetFont(get_wxFont(pointSize=6, faceName="Small Fonts"))
        self.createGuideline = None
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_SIZE, self.on_SIZE)

    @property
    def canvas(self):
        return self.Parent.canvas

    @property
    def zoom(self):
        return self.canvas.zoom

    @property
    def tickSize(self):
        z = self.zoom
        if z <= 0.1:
            return 1000.0
        if z <= 0.2:
            return 500.0
        if z <= 0.5:
            return 200.0
        if z <= 1:
            return 100.0
        if z <= 2:
            return 50.0
        if z <= 5:
            return 10.0
        if z <= 20:
            return 5.0
        return 1.0

    def OnEnterWindow(self, event):
        self.createGuideline = None
        event.Skip()

    def OnLeaveWindow(self, event):
        if self.HasCapture():
            self.ReleaseMouse()
        print("", end="")  # magic - make it work on mac!?
        event.Skip()

    def OnLeftDown(self, event):
        if event.ShiftDown():
            self.createGuideline = "Font"
        else:
            self.createGuideline = "Glyph"
        event.Skip()

    def OnLeftUp(self, event):
        self.createGuideline = None
        event.Skip()

    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self)
        dc.SetBackground(get_wxBrush(self.BackgroundColour))
        dc.Clear()
        self.Draw(dc)

    def OnEraseBackground(self, event):
        pass

    def on_SIZE(self, event):
        self.Refresh()
        event.Skip()

    def Draw(self, dc: wx.BufferedPaintDC):
        dc.SetPen(get_wxPen(self.ForegroundColour))
        dc.SetTextForeground(wx.BLACK)


class RulerHorizontal(Ruler):
    def __init__(self, parent):
        super().__init__(parent, name="RulerHorizontal")
        self.SetInitialSize((size.width, 20))

    @property
    def minValue(self):
        return self.canvas.screenToCanvasX(0)

    @property
    def maxValue(self):
        return self.canvas.screenToCanvasX(self.Size.width)

    def Draw(self, dc: wx.BufferedPaintDC):
        super().Draw(dc)
        w = self.Size.width
        h = self.Size.height
        dc.DrawLine(0, h - 1, w, h - 1)
        ts = self.tickSize
        tick = int(round(self.minValue / ts) * ts)
        while tick < self.maxValue:
            t = self.canvas.canvasToScreenX(tick)
            dc.DrawLine(t, 0, t, h)
            dc.DrawText(str(int(tick)), t + 2, 1)
            tick += ts


class RulerVertical(Ruler):
    def __init__(self, parent):
        super().__init__(parent, name="RulerVertical")
        self.SetInitialSize((20, size.height))

    @property
    def minValue(self):
        return self.canvas.screenToCanvasY(self.Size.height)

    @property
    def maxValue(self):
        return self.canvas.screenToCanvasY(0)

    def Draw(self, dc):
        super().Draw(dc)
        w = self.Size.width - 1
        h = self.Size.height
        dc.DrawLine(w, 0, w, h)
        ts = self.tickSize
        tick = int(round(self.minValue / ts) * ts)
        while tick < self.maxValue:
            t = self.canvas.canvasToScreenY(tick)
            dc.DrawLine(0, t, w, t)
            text = str(int(tick))
            txt_w, txt_h = dc.GetTextExtent(text)
            dc.DrawText(text, w - txt_w - 1, t - txt_h)
            tick += ts


class GlyphEditPanel(wx.Panel):
    def __init__(self, parent, doc):
        super().__init__(
            parent,
            ID,
            pos,
            size,
            style=wx.NO_BORDER | wx.TAB_TRAVERSAL,
            name="UfoFontWindow",
        )
        self.SetBackgroundColour(wx.Colour(245, 245, 245))
        sizer = wx.FlexGridSizer(3, 2, 0, 0)
        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(1)
        sizer.SetFlexibleDirection(wx.BOTH)
        sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.canvas = Canvas(self, doc=doc)
        self.rulerTop = RulerHorizontal(self)
        self.rulerLeft = RulerVertical(self)
        self.metric = GlyphMetricPanel(self)

        sizer.Add(0, 0)
        sizer.Add(self.rulerTop, 0, wx.EXPAND, 0)
        sizer.Add(self.rulerLeft, 0, wx.EXPAND, 0)
        sizer.Add(self.canvas, 1, wx.EXPAND, 0)
        sizer.Add(0, 0)
        sizer.Add(self.metric, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.SetSizer(sizer)
        self.Layout()
        self.hideMetric()

    def Destroy(self):
        wx.LogDebug("GlyphEditPanel.Destroy()")
        try:
            self.DestroyChildren()
        except wx.wxAssertionError:
            pass
        return super().Destroy()

    @property
    def rulerShown(self):
        return self.rulerTop.Shown or self.rulerLeft.Shown

    def showRuler(self, show=True):
        self.rulerTop.Show(show)
        self.rulerLeft.Show(show)
        self.SendSizeEvent()

    def hideRuler(self, hide=True):
        self.showRuler(not hide)

    @property
    def metricShown(self):
        return self.metric.Shown
    
    def showMetric(self, show=True):
        self.metric.Show(show)
        self.SendSizeEvent()

    def hideMetric(self, hide=True):
        self.showMetric(not hide)