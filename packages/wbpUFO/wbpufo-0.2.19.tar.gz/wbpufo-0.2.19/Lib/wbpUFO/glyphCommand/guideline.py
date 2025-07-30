"""
guideline
===============================================================================

Glyph Commands related to guidelines
"""
import logging

import wx
from wbDefcon import Color, Guideline

from .base import GlyphCommand
from .parameter import (
    ParamBoolRequired,
    ParamColour,
    ParamFloatRequired,
    ParamIntRequired,
    ParamStrRequired,
)

log = logging.getLogger(__name__)


class ClearGuides(GlyphCommand):
    name = "Clear all local guides"

    def _execute(self, glyph):
        glyph.clearGuidelines()


class AddGuidelineCommand(GlyphCommand):
    name = "Add local guideline"
    parameters = [
        ParamIntRequired("x", "Horizontal position (x)", 0),
        ParamIntRequired("y", "Vertical position (y)", 0),
        ParamFloatRequired("a", "Angle", 0.0),
        ParamStrRequired("n", "Name"),
        ParamColour("c", "Colour", wx.WHITE),
        ParamBoolRequired("r", "Replace existing guideline (by name)", True),
    ]

    def _execute(self, glyph):
        if self.n and self.r:
            for guideline in glyph.guidelines:
                if guideline.name == self.n:
                    guideline.x = self.x
                    guideline.y = self.y
                    guideline.angle = self.a
                    guideline.name = self.n
                    if self.c == wx.WHITE:
                        guideline.color = None
                    else:
                        guideline.color = Color.from_wx(self.c)
                    return
        guideline = Guideline(guidelineDict=dict(x=self.x, y=self.y, angle=self.a))
        if self.n:
            guideline.name = self.n
        if self.c != wx.WHITE:
            guideline.color = Color.from_wx(self.c)
        glyph.appendGuideline(guideline)


class RemoveGuidelineCommand(GlyphCommand):
    name = "Remove guideline (by name)"
    parameters = [ParamStrRequired("n", "Name")]

    def _execute(self, glyph):
        for guideline in reversed(glyph.guidelines):
            if guideline.name == self.n:
                glyph.removeGuideline(anchor)
