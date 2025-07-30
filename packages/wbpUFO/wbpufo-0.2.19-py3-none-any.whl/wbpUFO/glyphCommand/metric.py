"""
metric
===============================================================================

Glyph Commands related to glyph metric
"""
from .base import GlyphCommand
from .parameter import (
    ParamBoolRequired,
    ParamEnumeration,
    ParamIntRequired,
)


class SetWidthCommand(GlyphCommand):
    name = "Set width"
    ALLIGN_CENTER = 0
    ALLIGN_LEFT = 1
    ALLIGN_RIGHT = 2
    ALLIGN_NONE = 3
    DISTRIBUTE_DIFF = 4
    parameters = [
        ParamIntRequired("w", "Set fixed width", 500),
        ParamEnumeration(
            "m",
            "Set margins",
            [
                "Center glyph",
                "Allign to left margin",
                "Allign to right margin",
                "Keep as is",
                "Distribure difference",
            ],
            ALLIGN_CENTER,
        ),
        ParamBoolRequired("c", "Preserve Composites", True),
    ]

    def _execute(self, glyph):
        old_width = glyph.width
        glyph.width = self.w
        if self.m == self.ALLIGN_NONE:
            return
        bounds = glyph.bounds
        if bounds:
            x0, y0, x1, y1 = bounds
            if self.m == self.ALLIGN_LEFT:
                distance = (-x0, 0)
            elif self.m == self.ALLIGN_RIGHT:
                distance = (self.w - x1, 0)
            elif self.m == self.ALLIGN_CENTER:
                distance = ((self.w - x0 - x1) / 2, 0)
            elif self.m == self.DISTRIBUTE_DIFF:
                distance = (0, 0)
                if old_width != self.w:
                    diff = self.w - old_width
                    distance = (round(diff/2), 0)

            if distance != (0, 0):
                glyph.moveBy(distance)
                if self.c:
                    font = glyph.font
                    if font and hasattr(font, "componentReferences"):
                        componentReferences = font.componentReferences
                        if glyph.name in componentReferences:
                            distBack = (-distance[0], 0)
                            for glyphName in componentReferences[glyph.name]:
                                compositeGlyph = font[glyphName]
                                for component in compositeGlyph.components:
                                    if component.baseGlyph == glyph.name:
                                        component.moveBy(distBack)


class CenterGlyphCommand(GlyphCommand):
    name = "Center glyph"
    parameters = [ParamBoolRequired("c", "Preserve Composites", True)]

    def _execute(self, glyph):
        bounds = glyph.bounds
        if bounds:
            x0, y0, x1, y1 = bounds
            distance = ((glyph.width - x0 - x1) / 2, 0)
            if distance != (0, 0):
                glyph.moveBy(distance)
                if self.c:
                    font = glyph.font
                    if font and hasattr(font, "componentReferences"):
                        componentReferences = font.componentReferences
                        if glyph.name in componentReferences:
                            distBack = (-distance[0], 0)
                            for glyphName in componentReferences[glyph.name]:
                                compositeGlyph = font[glyphName]
                                for component in compositeGlyph.components:
                                    if component.baseGlyph == glyph.name:
                                        component.moveBy(distBack)


class SetLeftMarginCommand(GlyphCommand):
    name = "Set left margin"
    ACTION_SET_EQUAL = 0
    ACTION_INCREASE = 1
    ACTION_DECREASE = 2
    PRESERVE_RIGHT_MARGIN = 0
    PRESERVE_WIDTH = 1
    parameters = [
        ParamEnumeration(
            "a",
            "Action",
            ["Set equal to", "Increase by", "Decrease by"],
            ACTION_SET_EQUAL,
        ),
        ParamIntRequired("v", "Units", 0),
        ParamEnumeration(
            "p", "Preserve metric", ["Right margin", "Width"], PRESERVE_RIGHT_MARGIN
        ),
        ParamBoolRequired("c", "Preserve Composites", True),
    ]

    def _execute(self, glyph):
        bounds = glyph.bounds
        if bounds:
            x0, y0, x1, y1 = bounds
            if self.p == self.PRESERVE_RIGHT_MARGIN:
                right_margin = glyph.width - x1
            if self.a == self.ACTION_SET_EQUAL:
                distance = (self.v - x0, 0)
            elif self.a == self.ACTION_INCREASE:
                distance = (self.v, 0)
            elif self.a == self.ACTION_DECREASE:
                distance = (-self.v, 0)
            if distance != (0, 0):
                glyph.moveBy(distance)
                if self.c:
                    font = glyph.font
                    if font and hasattr(font, "componentReferences"):
                        componentReferences = font.componentReferences
                        if glyph.name in componentReferences:
                            distBack = (-distance[0], 0)
                            for glyphName in componentReferences[glyph.name]:
                                compositeGlyph = font[glyphName]
                                for component in compositeGlyph.components:
                                    if component.baseGlyph == glyph.name:
                                        component.moveBy(distBack)
                if self.p == self.PRESERVE_RIGHT_MARGIN:
                    bounds_new = glyph.bounds
                    if bounds_new:
                        x0, y0, x1, y1 = bounds_new
                        glyph.width = x1 + right_margin


class SetRightMarginCommand(GlyphCommand):
    name = "Set right margin"
    ACTION_SET_EQUAL = 0
    ACTION_INCREASE = 1
    ACTION_DECREASE = 2
    PRESERVE_LEFT_MARGIN = 0
    PRESERVE_WIDTH = 1
    parameters = [
        ParamEnumeration(
            "a",
            "Action",
            ["Set equal to", "Increase by", "Decrease by"],
            ACTION_SET_EQUAL,
        ),
        ParamIntRequired("v", "Units", 0),
        ParamEnumeration(
            "p", "Preserve metric", ["Left margin", "Width"], PRESERVE_LEFT_MARGIN
        ),
        ParamBoolRequired("c", "Preserve Composites", True),
    ]

    def _execute(self, glyph):
        bounds = glyph.bounds
        if bounds:
            x0, y0, x1, y1 = bounds
            rignt_margin_old = glyph.width - x1
            if self.a == self.ACTION_SET_EQUAL:
                right_margin = self.v
            elif self.a == self.ACTION_INCREASE:
                right_margin = rignt_margin_old + self.v
            elif self.a == self.ACTION_DECREASE:
                right_margin = rignt_margin_old - self.v
            if self.p == self.PRESERVE_WIDTH:
                distance = (rignt_margin_old - right_margin, 0)
                if distance != (0, 0):
                    glyph.moveBy(distance)
                    if self.c:
                        font = glyph.font
                        if font and hasattr(font, "componentReferences"):
                            componentReferences = font.componentReferences
                            if glyph.name in componentReferences:
                                distBack = (-distance[0], 0)
                                for glyphName in componentReferences[glyph.name]:
                                    compositeGlyph = font[glyphName]
                                    for component in compositeGlyph.components:
                                        if component.baseGlyph == glyph.name:
                                            component.moveBy(distBack)
            elif self.p == self.PRESERVE_LEFT_MARGIN:
                glyph.width = x1 + right_margin
