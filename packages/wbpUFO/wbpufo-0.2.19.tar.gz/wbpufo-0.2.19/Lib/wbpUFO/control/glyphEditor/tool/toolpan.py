"""
toolpan
===============================================================================
"""

import wx

from .base import GlyphTool


class ToolPan(GlyphTool):
    cursor = wx.Cursor(wx.CURSOR_HAND)

    def on_MOTION(self, event):
        GlyphTool.on_MOTION(self, event)
        if event.Dragging():
            canvas = self.canvas
            canvas.Scroll(
                canvas.ViewStart[0] - (self.x - self.xPrev),
                canvas.ViewStart[1] - (self.y - self.yPrev),
            )
            canvas.updateRuler()
        event.Skip()
