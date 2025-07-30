"""
toolscale
===============================================================================
"""

from .base import WORKING, TransformBaseTool


class ToolScale(TransformBaseTool):
    def __init__(self, parent):
        super().__init__(parent)
        self.angleSnap = 45
        self.scalePrev = (1, 1)
        self.ratio = 100

    @property
    def scale(self):
        if self.state == WORKING:
            sx = 1 + (self.center[0] - self.canvas.screenToCanvasX(self.x)) / self.ratio
            sy = 1 + (self.center[1] - self.canvas.screenToCanvasY(self.y)) / self.ratio
            if self.shiftDown:
                a = abs(int(self.angle))
                if a in (0, 180):
                    sy = 1
                elif a in (90, 270):
                    sx = 1
                elif a in (45, 135, 225, 315):
                    sx = sy = (sx + sy) / 2
            return (sx, sy)
        return (1, 1)

    # -------------------------------------------------------------------------
    # Event handler methods
    # -------------------------------------------------------------------------

    def on_LEFT_UP(self, event):
        self.scalePrev = (1, 1)
        super().on_LEFT_UP(event)

    def on_MOTION(self, event):
        TransformBaseTool.on_MOTION(self, event)
        if event.Dragging() and self.state == WORKING:
            scale = self.scale
            delta = (self.scalePrev[0] - scale[0], self.scalePrev[1] - scale[1])
            if delta[0] or delta[1]:
                delta = (1 + delta[0], 1 + delta[1])
                glyph = self.glyph
                if self.isAnySelected():
                    for contour in glyph:
                        for point in contour:
                            if point.selected:
                                point.scaleBy(delta, self.center)
                                self.contoursChanged = True
                    for anchor in glyph.anchors:
                        if anchor.selected:
                            anchor.scaleBy(delta, self.center)
                            self.anchorsChanged = True
                    for component in glyph.components:
                        if component.selected:
                            component.scaleBy(delta, self.center)
                            self.componentsChanged = True
                else:
                    # todo: check locked plains
                    glyph.scaleBy(delta, self.center)
                self.canvas.Refresh()
            self.scalePrev = scale
        event.Skip()
