"""
composite
===============================================================================

Glyph Commands related to composites
"""
from __future__ import annotations

from typing import TYPE_CHECKING

# from glyphConstruction import (
#     GlyphConstructionBuilder,
#     ParseGlyphConstructionListFromString,
# )
from fontTools.misc.transform import Identity
from ufo2ft.filters.flattenComponents import _flattenComponent

from .base import GlyphCommand
from .parameter import ParamBoolRequired, ParamFilepathRequired

if TYPE_CHECKING:
    from wbDefcon.objects.component import Component
    from wbDefcon.objects.glyph import Glyph


class DecomposeCommand(GlyphCommand):
    name = "Decompose"
    parameters = [ParamBoolRequired("t", "Transformed components only", False)]

    def _execute(self, glyph: Glyph):
        if not glyph.components:
            return
        if not self.t:
            glyph.decomposeAllComponents()
            return
        for component in reversed(glyph.components):
            if component.transformation[:4] != Identity[:4]:
                glyph.decomposeComponent(component)


class ClearComponentsCommand(GlyphCommand):
    name = "Clear all components"

    def _execute(self, glyph: Glyph):
        glyph.clearComponents()


class FlattenComponentsCommand(GlyphCommand):
    name = "Flatten all components"

    def _execute(self, glyph: Glyph):
        component: Component
        if not glyph.components:
            return
        font = glyph.font
        glyphSet = font.layers.defaultLayer
        pen = glyph.getPen()
        for component in list(glyph.components):
            flattened_tuples = _flattenComponent(glyphSet, component, found_in=glyph)
            if len(flattened_tuples) == 1 and flattened_tuples[0] == (
                component.baseGlyph,
                component.transformation,
            ):
                continue
            glyph.removeComponent(component)
            for flattened_tuple in flattened_tuples:
                pen.addComponent(*flattened_tuple)


# class UpdateCompositeCommand(GlyphCommand):
#     name = "Update composite"
#     parameters = [ParamFilepathRequired("c", "Glyph construction file", default="")]

#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self._constructions = None

#     @property
#     def constructions(self):
#         if not self._constructions:
#             constructions = ParseGlyphConstructionListFromString(self.c)
#             self._constructions = dict(
#                 (c.split("=", 1)[0].strip(), c) for c in constructions
#             )
#         return self._constructions

#     def _execute(self, glyph):
#         if glyph.components and glyph.name in self.constructions:
#             name = glyph.name
#             font = glyph.font
#             constructionGlyph = GlyphConstructionBuilder(self.constructions[name], font)
#             # newGlyph = font.newGlyph(name)
#             glyph.clearComponents()
#             constructionGlyph.draw(glyph.getPen())
#             glyph.unicode = constructionGlyph.unicode
#             # newGlyph.note = constructionGlyph.note
#             glyph.width = constructionGlyph.width
