"""
anchor
===============================================================================

Glyph Commands related to glyph anchors
"""
import wx

from wbDefcon import Anchor, Color, Glyph
from ufo2ft.filters.propagateAnchors import _propagate_glyph_anchors
from ufo2ft.util import OpenTypeCategories

from .base import GlyphCommand
from .parameter import (
    ParamBoolRequired,
    ParamStrRequired,
    ParamColour,
    ParamIntRequired,
)


class AddAnchorCommand(GlyphCommand):
    """
    Glyph Command to add anchors to glyphs
    """
    x:int
    y:int
    n:str
    c:wx.Colour
    r:bool
    name = "Add anchor"
    parameters = [
        ParamIntRequired("x", "Horizontal position (x)", 0),
        ParamIntRequired("y", "Vertical position (y)", 0),
        ParamStrRequired("n", "Name"),
        ParamColour("c", "Colour", wx.WHITE),
        ParamBoolRequired("r", "Replace existing anchor (by name)", False),
    ]

    def _execute(self, glyph: Glyph):
        for anchor in glyph.anchors:
            if anchor.name == self.n:
                if self.r:
                    anchor.holdNotifications()
                    anchor.x = self.x
                    anchor.y = self.y
                    if self.c != wx.WHITE:
                        anchor.color = Color.from_wx(self.c)
                    anchor.releaseHeldNotifications()
                return
        anchor = Anchor(anchorDict=dict(name=self.n, x=self.x, y=self.y))
        if self.c != wx.WHITE:
            anchor.color = Color.from_wx(self.c)
        glyph.appendAnchor(anchor)


class RemoveAnchorCommand(GlyphCommand):
    """
    Glyph Command to remove anchors by name from glyphs
    """
    n:str
    name = "Remove anchor (by name)"
    parameters = [ParamStrRequired("n", "Name")]

    def _execute(self, glyph: Glyph):
        for anchor in reversed(glyph.anchors):
            if anchor.name == self.n:
                glyph.removeAnchor(anchor)


class ClearAnchorCommand(GlyphCommand):
    """
    Glyph Command to remove all anchors from glyphs
    """
    name = "Clear all anchors"

    def _execute(self, glyph: Glyph):
        glyph.clearAnchors()


class PropagateAnchorsCommand(GlyphCommand):
    """
    Propagate anchors from base glyphs to a given composite
    glyph, and to all composite glyphs used in between.
    """
    name = "Propagate anchors"

    def _execute(self, glyph: Glyph):
        if not glyph.components:
            return
        font = glyph.font
        modified = set()
        processed = set()
        categories = OpenTypeCategories.load(font)
        _propagate_glyph_anchors(font.layers.defaultLayer, glyph, processed, modified, categories)
