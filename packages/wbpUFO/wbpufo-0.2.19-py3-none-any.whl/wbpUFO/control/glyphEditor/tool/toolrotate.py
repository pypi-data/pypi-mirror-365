"""
toolrotate
===============================================================================
"""

from .base import WORKING, TransformBaseTool


class ToolRotate(TransformBaseTool):
    def __init__(self, parent):
        TransformBaseTool.__init__(self, parent)
        self.anglePrev = 0
        self.angleSnap = 15

    # -------------------------------------------------------------------------
    # Event handler methods
    # -------------------------------------------------------------------------
    def on_LEFT_UP(self, event):
        self.anglePrev = 0
        TransformBaseTool.on_LEFT_UP(self, event)

    def on_MOTION(self, event):
        TransformBaseTool.on_MOTION(self, event)
        if event.Dragging() and self.state == WORKING:
            angle = self.angle
            delta = self.anglePrev - angle
            if delta:
                glyph = self.glyph
                if self.isAnySelected():
                    for contour in glyph:
                        for point in contour:
                            if point.selected:
                                point.rotateBy(delta, self.center)
                                self.contoursChanged = True
                    for anchor in glyph.anchors:
                        if anchor.selected:
                            anchor.rotateBy(delta, self.center)
                            self.anchorsChanged = True
                    for component in glyph.components:
                        if component.selected:
                            component.rotateBy(delta, self.center)
                            self.componentsChanged = True
                else:
                    # todo: check locked plains
                    glyph.rotateBy(delta, self.center)
                self.canvas.Refresh()
            self.anglePrev = angle
        event.Skip()
