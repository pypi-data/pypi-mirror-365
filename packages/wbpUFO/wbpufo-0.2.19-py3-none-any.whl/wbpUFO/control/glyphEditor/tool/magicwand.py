"""
magicwand
===============================================================================
"""

import wx

from ..cursor import cursors
from .base import GlyphTool


class MagicWand(GlyphTool):
    cursor = cursors["MagicWand"]

    def __init__(self, parent):
        GlyphTool.__init__(self, parent)
        self.addToSelection = False
        # Mouse Events
        self.Bind(wx.EVT_MOTION, self.on_MOTION)
        # Keyboard Events
        self.Bind(wx.EVT_KEY_DOWN, self.on_KEY_DOWN)
        self.Bind(wx.EVT_KEY_UP, self.on_KEY_UP)

    def reset(self):
        super(MagicWand, self).reset()
        self.addToSelection = False

    def on_LEFT_DOWN(self, event):
        GlyphTool.on_LEFT_DOWN(self, event)
        x = self.canvas.screenToCanvasX(event.GetX())
        y = self.canvas.screenToCanvasY(event.GetY())
        contourDistance = {}
        for contour in self.glyph:
            minDistance = 100000
            for point in contour:
                minDistance = min(minDistance, point.distance((x, y)))
            contourDistance[minDistance] = contour
        if not self.addToSelection:
            self.unselectAll()
        contourDistance[min(contourDistance.keys())].selected = True
        self.canvas.Refresh()
        event.Skip()

    def on_MOTION(self, event):
        if not event.ControlDown():
            self.canvas.unselectTool()
        GlyphTool.on_MOTION(self, event)

    def on_KEY_DOWN(self, event):
        unicodeKey = event.GetUnicodeKey()
        if unicodeKey == wx.WXK_NONE:
            key = event.KeyCode
        else:
            key = chr(unicodeKey)
        if key == " ":  # Space pressed
            self.canvas.selectTool("ToolZoom")
        elif key == wx.WXK_SHIFT:
            self.addToSelection = True
        event.Skip()

    def on_KEY_UP(self, event):
        unicodeKey = event.GetUnicodeKey()
        if unicodeKey == wx.WXK_NONE:
            key = event.KeyCode
        else:
            key = chr(unicodeKey)
        if key == wx.WXK_SHIFT:
            self.addToSelection = False
        event.Skip()
