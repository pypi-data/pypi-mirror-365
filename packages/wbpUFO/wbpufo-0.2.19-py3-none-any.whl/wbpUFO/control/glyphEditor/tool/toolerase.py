"""
toolerase
===============================================================================

Implementation of the erase tool for the glyph editor
"""
from wbDefcon import Anchor, Component, Guideline, Point

from ..cursor import cursors
from .base import IDLE, GlyphTool


class ToolErase(GlyphTool):
    """
    Tool to erase points, anchors, components, guidelines
    """
    cursor = cursors["Erase"]

    def setCursor(self):
        if self.subject is None:
            self.canvas.SetCursor(cursors["Erase"])
        elif isinstance(self.subject, Point):
            self.canvas.SetCursor(cursors["ErasePoint"])
        elif isinstance(self.subject, Anchor):
            self.canvas.SetCursor(cursors["EraseAnchor"])
        elif isinstance(self.subject, Component):
            self.canvas.SetCursor(cursors["EraseComponent"])
        elif isinstance(self.subject, Guideline):
            self.canvas.SetCursor(cursors["EraseGuideline"])

    # -------------------------------------------------------------------------
    # Event handler methods
    # -------------------------------------------------------------------------

    def on_LEFT_DOWN(self, event):
        super().on_LEFT_DOWN(event)
        glyph = self.glyph
        if glyph is not None and self.subject is not None:
            glyph.undoManager.saveState()
            if isinstance(self.subject, Point):
                point = self.subject
                for contour in glyph:
                    segmentIndex = contour.segmentIndex(point)
                    if segmentIndex >= 0:
                        if point.segmentType is None:
                            # erase off-curve point, convert to line
                            segment = contour.segments[segmentIndex]
                            segment[-1].segmentType = "line"
                            segment[-1].smooth = False
                            for p in segment[:-1]:
                                contour.removePoint(p)
                        else:
                            # erase on-curve point, remove the segment
                            contour.removeSegment(segmentIndex, True)
                            if len(contour) == 0:
                                glyph.removeContour(contour)
                        self.contoursChanged = True
            elif isinstance(self.subject, Anchor):
                glyph.removeAnchor(self.subject)
                self.anchorsChanged = True
            elif isinstance(self.subject, Component):
                glyph.removeComponent(self.subject)
                self.componentsChanged = True
            elif isinstance(self.subject, Guideline):
                if self.subject.glyph is None:
                    glyph.font.removeGuideline(self.subject)
                    self.fontGuidelinesChanged = True
                else:
                    glyph.removeGuideline(self.subject)
                    self.glyphGuidelinesChanged = True
            if self.contoursChanged or self.componentsChanged:
                glyph.destroyRepresentation("outlineErrors")
            self.postNotifications()
            self.canvas.Refresh()
        self.state = IDLE
        event.Skip()

    def on_MOTION(self, event):
        super().on_MOTION(event)
        if self.glyph is not None:
            if self.state == IDLE:
                self.hitTest()
                self.setCursor()
        event.Skip()
