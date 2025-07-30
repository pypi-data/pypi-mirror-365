"""
parameter
===============================================================================

Glyph-Command-Parameters
"""
import logging

import wx
from wx.propgrid import (
    BoolProperty,
    ColourProperty,
    EditEnumProperty,
    EnumProperty,
    FileProperty,
    FlagsProperty,
    FloatProperty,
    IntProperty,
    StringProperty,
)


log = logging.getLogger(__name__)


class GlyphCmdParameter:
    """Base class for Glyph-Command-Parameters"""

    def __init__(self, name, type, label=None, default=None, allowNone=True):
        self.name = name
        self.type = type
        if label:
            self.label = label
        else:
            self.label = self.name
        self.allowNone = allowNone
        if default is not None:
            assert isinstance(default, self.type)
        elif not self.allowNone:
            assert default is not None
        self.default = default

    def __repr__(self):
        return "<%s: name=%s>" % (self.__class__.__name__, self.name)

    def fromString(self, value):
        log.debug("GlyphCmdParameter.fromString(%r)", value)
        return self.type(value)

    def toString(self, value):
        log.debug("GlyphCmdParameter %r toString(%r)", self.name, value)
        return str(value)

    def pgProperty(self, value):
        return NotImplemented

class ParamIntRequired(GlyphCmdParameter):
    """Required integer parameter"""

    def __init__(self, name, label=None, default=0):
        super().__init__(name, int, label, default, allowNone=False)

    def pgProperty(self, value):
        prop = IntProperty(self.label, self.name, value)
        prop.SetEditor("SpinCtrl")
        return prop


class ParamFloatRequired(GlyphCmdParameter):
    """Required float parameter"""

    def __init__(self, name, label=None, default=0):
        super().__init__(name, float, label, default, allowNone=False)

    def pgProperty(self, value):
        return FloatProperty(self.label, self.name, value)


class ParamStr(GlyphCmdParameter):
    """Optional string parameter"""

    def __init__(self, name, label=None, default=None):
        super().__init__(name, str, label, default, allowNone=True)

    def pgProperty(self, value):
        return StringProperty(self.label, self.name, value)


class ParamStrRequired(GlyphCmdParameter):
    """Required string parameter"""

    def __init__(self, name, label=None, default=""):
        super().__init__(name, str, label, default, allowNone=False)

    def pgProperty(self, value):
        return StringProperty(self.label, self.name, value)


class ParamBoolRequired(GlyphCmdParameter):
    """Required boolean parameter"""

    def __init__(self, name, label=None, default=False):
        super().__init__(name, bool, label, default, allowNone=False)

    def pgProperty(self, value):
        prop = BoolProperty(self.label, self.name, value)
        prop.SetEditor("CheckBox")
        return prop


class ParamEnumeration(GlyphCmdParameter):
    def __init__(self, name, label=None, choices=None, default=0):
        super().__init__(name, int, label, default, allowNone=False)
        self.labels = choices or []

    def pgProperty(self, value):
        return EnumProperty(
            self.label, self.name, self.labels, range(len(self.labels)), value
        )


class ParamEditableEnumeration(GlyphCmdParameter):
    def __init__(self, name, label=None, choices=None, default=None):
        self.labels = choices or []
        if isinstance(default, int) and default in range(len(self.labels)):
            default = self.labels[default]
        super().__init__(name, str, label=label, default=default, allowNone=False)

    def toString(self, value):
        if isinstance(value, str):
            return value
        if isinstance(value, int) and value in range(len(self.labels)):
            return self.labels[value]

    def pgProperty(self, value):
        if isinstance(value, int) and value in range(len(self.labels)):
            value = self.labels[value]
        return EditEnumProperty(
            self.label, self.name, self.labels, range(len(self.labels)), value
        )


class ParamFlags(GlyphCmdParameter):
    def __init__(self, name, label=None, choices=None, default=0):
        super().__init__(name, int, label, default, allowNone=False)
        self.labels = choices or []

    def pgProperty(self, value):
        return FlagsProperty(
            self.label,
            self.name,
            self.labels,
            [2 ** i for i in range(len(self.labels))],
            value,
        )


class ParamColour(GlyphCmdParameter):
    def __init__(self, name, label=None, default=wx.RED):
        super().__init__(name, wx.Colour, label, default, allowNone=False)

    def fromString(self, value):
        colour = self.type()
        colour.Set(value)
        return colour

    def toString(self, value):
        return value.GetAsString(wx.C2S_CSS_SYNTAX)

    def pgProperty(self, value):
        return ColourProperty(self.label, self.name, value)


class ParamFilepathRequired(ParamStrRequired):
    def pgProperty(self, value):
        return FileProperty(self.label, self.name, value)
