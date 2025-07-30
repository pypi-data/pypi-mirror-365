"""
toolstartpoint
===============================================================================

Implementation of the set start point tool for the glyph editor
"""
import logging

from wbDefcon import Point

from ..cursor import cursors
from .base import GlyphTool

log = logging.getLogger(__name__)


class ToolStartpoint(GlyphTool):
    """
    Tool to set start point of contours
    """
    cursor = cursors["EditStartpoint"]

    def hitTest(self):
        # check for pointing Stuff under cursor
        canvas_x = self.canvas.screenToCanvasX(self.x)
        canvas_y = self.canvas.screenToCanvasY(self.y)
        pointed = None
        self.subject = None
        # perform hit test on On Curve Points
        plain = self.activeStack.get("OnCurvePoints")
        if plain.visible and not plain.locked:
            pointed = plain.hitTest(canvas_x, canvas_y)
            if pointed is not None and pointed != self.subject:
                self.subject = pointed

    def setCursor(self):
        if isinstance(self.subject, Point):
            self.canvas.SetCursor(cursors["EditPoint"])
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
            glyph = self.glyph
            for contour in glyph:
                if self.subject in contour:
                    glyph.undoManager.saveState()
                    contour.setStartPoint(contour.index(self.subject))
