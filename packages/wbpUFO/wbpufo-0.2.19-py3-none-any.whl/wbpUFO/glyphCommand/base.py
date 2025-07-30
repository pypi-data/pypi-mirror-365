"""
base
===============================================================================

Base for all Glyph Commands
"""
# pylint: disable=invalid-name

from __future__ import annotations
import logging
from typing import List

from .parameter import GlyphCmdParameter, ParamEditableEnumeration

log = logging.getLogger(__name__)


class GlyphCommand:
    """Base class for Glyph-Commands"""

    name: str = "Command"
    parameters: List[GlyphCmdParameter] = []

    def __init__(self, **kwargs):
        self._setupParameters()
        for name, value in kwargs.items():
            assert self.has_parameter(name)
            assert isinstance(
                value, self.parameter(name).type
            ), "Expected instance of %r, got %r" % (self.parameter(name).type, value)
            setattr(self, name, value)

    def __str__(self) -> str:
        return "%s: %s" % (self.name, self.paramString)

    def __repr__(self) -> str:
        return "<%s: %s>" % (self.__class__.__name__, self.paramString)

    def __setattr__(self, name: str, value):
        parameter = self.get_parameter(name)
        if isinstance(parameter, ParamEditableEnumeration) and isinstance(value, int):
            value = parameter.labels[value]
        super().__setattr__(name, value)

    @property
    def paramString(self) -> str:
        """
        String representation of all parameters.
        """
        params = []
        for param in self.parameters:
            params.append(
                "%s=%s" % (param.name, param.toString(getattr(self, param.name)))
            )
        return "; ".join(params)

    @classmethod
    def parameter(cls, name: str) -> GlyphCmdParameter:
        for parameter in cls.parameters:
            if parameter.name == name:
                return parameter
        raise KeyError('Parameter "%s" not defined' % name)

    @classmethod
    def fromString(cls, string: str):
        if cls.parameters:
            params = dict(s.strip().split("=") for s in string.split(";"))
            for name in params:
                params[name] = cls.parameter(name).fromString(params[name])
        else:
            params = {}
        return cls(**params)

    @property
    def pgProperties(self):
        return [p.pgProperty(getattr(self, p.name)) for p in self.parameters]

    def _setupParameters(self) -> None:
        for parameter in self.parameters:
            assert isinstance(parameter, GlyphCmdParameter), (
                "expected <GlyphCmdParameter>, got %r" % parameter
            )
            setattr(self, parameter.name, parameter.default)

    def _checkParameters(self) -> bool:
        for parameter in self.parameters:
            if not hasattr(self, parameter.name):
                log.debug(
                    "Paramerter check failed: command %r has no parameter %r",
                    self.name,
                    parameter.name,
                )
                return False
            value = getattr(self, parameter.name)
            if value is None and not parameter.allowNone:
                log.debug(
                    "Paramerter check for command %r failed: %r is None, which is not allowed",
                    self.name,
                    parameter.name,
                )
                return False
            if isinstance(parameter, ParamEditableEnumeration):
                if isinstance(value, int):
                    return value in range(len(parameter.labels))
            if not isinstance(value, parameter.type):
                log.debug(
                    "Paramerter check for command %r failed: %r is of type %r, but %r is expected",
                    self.name,
                    parameter.name,
                    type(value),
                    parameter.type,
                )
                return False
        return True

    def has_parameter(self, name:str) -> bool:
        for parameter in self.parameters:
            if parameter.name == name:
                return True
        return False

    def get_parameter(self, name:str, default=None):
        for parameter in self.parameters:
            if parameter.name == name:
                return parameter
        return default

    def _execute(self, glyph):
        """override this in sub classes"""
        raise NotImplementedError(
            f"_execute method of {self.__class__.__name__} not implemented"
        )

    def execute(self, glyph) -> None:
        if self._checkParameters():
            self._execute(glyph)
