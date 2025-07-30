"""
layer
===============================================================================

Glyph Commands related to layers
"""
import logging

from wbDefcon.objects.glyph import Glyph

from .base import GlyphCommand
from .parameter import ParamEditableEnumeration

log = logging.getLogger(__name__)


class CopyToLayer(GlyphCommand):
    name = "Copy from default Layer to other Layer"
    parameters = [
        ParamEditableEnumeration(
            "t",
            "Target Layer",
            ["public.background", "private.temp"],
            default="public.background",
        )
    ]

    def _execute(self, glyph):
        font = glyph.font
        if self.t in font.layers:
            targetLayer = font.layers[self.t]
        else:
            targetLayer = font.newLayer(self.t)
        if glyph.name in targetLayer:
            targetGlyph = targetLayer[glyph.name]
        else:
            targetGlyph = targetLayer.newGlyph(glyph.name)
        targetGlyph.copyDataFromGlyph(glyph)


class CopyFromLayer(GlyphCommand):
    name = "Copy from other Layer to default Layer"
    parameters = [
        ParamEditableEnumeration(
            "s", "Source Layer", ["public.background"], default="public.background"
        )
    ]

    def _execute(self, glyph):
        font = glyph.font
        if self.s in font.layers:
            sourceLayer = font.layers[self.s]
            if glyph.name in sourceLayer:
                sourceGlyph = sourceLayer[glyph.name]
                glyph.copyDataFromGlyph(sourceGlyph)
            else:
                log.warning("Glyph %s not found on layer %r", glyph.name, self.s)
        else:
            log.warning("Layer %r for glyph %s does not exist", self.s, glyph.name)


class ExchangeWithLayer(GlyphCommand):
    name = "Exchange default Layer with other Layer"
    parameters = [
        ParamEditableEnumeration(
            "o", "Other Layer", ["public.background"], default="public.background"
        )
    ]

    def _execute(self, glyph):
        font = glyph.font
        name = glyph.name
        if self.o in font.layers:
            targetLayer = font.layers[self.o]
        else:
            targetLayer = font.newLayer(self.o)
        # move glyph from targetLayer to tempGlyph
        tempGlyph = None
        if name in targetLayer:
            tempGlyph = Glyph()
            targetGlyph = targetLayer[name]
            tempGlyph.copyDataFromGlyph(targetGlyph)
            targetGlyph.clear()
        else:
            targetGlyph = targetLayer.newGlyph(name)
        # move glyph from default to targetLayer
        targetGlyph.copyDataFromGlyph(glyph)
        glyph.clear()
        # move glyph from tempGlyph to active layer
        if tempGlyph is not None:
            glyph.copyDataFromGlyph(tempGlyph)


class ClearLayer(GlyphCommand):
    name = "Clear Layer"
    parameters = [
        ParamEditableEnumeration(
            "l", "Layer", ["public.background"], default="public.background"
        )
    ]

    def _execute(self, glyph):
        font = glyph.font
        if self.l in font.layers:
            layer = font.layers[self.l]
            if glyph.name in layer:
                del layer[glyph.name]
                if len(layer) == 0:
                    del font.layers[self.l]
