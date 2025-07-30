"""
toolreverse
===============================================================================

Implementation of the reverse contour direction tool for the glyph editor
"""
import logging

from wbDefcon.pens import ContourHit

from ..cursor import cursors
from .base import GlyphTool

log = logging.getLogger(__name__)


class ToolReverse(GlyphTool):
    """
    Tool to reverse direction of contours
    """
    cursor = cursors["EditContourDirection"]

    def hitTest(self):
        # check for pointing Stuff under cursor
        canvas_x = self.canvas.screenToCanvasX(self.x)
        canvas_y = self.canvas.screenToCanvasY(self.y)
        pointed = None
        self.subject = None
        # perform hit test on Glyph Outline
        plain = self.activeStack.get("GlyphOutline")
        if plain.visible and not plain.locked:
            pointed = plain.hitTest(canvas_x, canvas_y)
            if pointed is not None and pointed != self.subject:
                self.subject = pointed

    def setCursor(self):
        if isinstance(self.subject, ContourHit):
            self.canvas.SetCursor(cursors["EditContour"])
        else:
            self.canvas.SetCursor(self.cursor)

    # -------------------------------------------------------------------------
    # Event handler methods
    # -------------------------------------------------------------------------

    def on_MOTION(self, event):
        super().on_MOTION(event)
        glyph = self.glyph
        if glyph is not None:
            self.hitTest()
            self.setCursor()
        event.Skip()

    def on_LEFT_DOWN(self, event):
        if self.subject is not None:
            self.subject.contour.reverse()
