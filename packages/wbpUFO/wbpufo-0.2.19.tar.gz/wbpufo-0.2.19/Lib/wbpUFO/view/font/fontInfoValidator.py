"""
fontInfoValidator
===============================================================================

"""
import logging
import re
from string import digits, whitespace

import wx
from fontTools.ufoLib import (
    fontInfoAttributesVersion3ValueData,
    validateFontInfoVersion3ValueForAttribute,
)

log = logging.getLogger(__name__)


class FontInfoBaseValidator(wx.Validator):
    def __init__(self, getFontInfo):
        super().__init__()
        self._getFontInfo = getFontInfo
        self._fontInfo = None
        self._valueType = None
        # log.debug("FontInfoBaseValidator.__init__() done")

    def __repr__(self):
        return "<%s for %r>" % (self.__class__.__name__, self.Window.Name)

    @property
    def fontInfo(self):
        if not self._fontInfo:
            self._fontInfo = self._getFontInfo()
        return self._fontInfo

    @property
    def valueType(self):
        if self._valueType is None:
            ctrl = self.GetWindow()
            if ctrl:
                self._valueType = fontInfoAttributesVersion3ValueData[ctrl.Name]["type"]
        return self._valueType

    def Clone(self):
        return self.__class__(self._getFontInfo)

    def Validate(self, win):
        return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True


class FontInfoTextCtrlValidator(FontInfoBaseValidator):
    def __init__(self, getFontInfo):
        super().__init__(getFontInfo)
        self.Bind(wx.EVT_CHAR, self.on_char)

    def _getValueFromControl(self):
        ctrl:wx.TextCtrl = self.GetWindow()
        value:str = ctrl.Value
        if value == wx.EmptyString:
            return None
        valueType = self.valueType
        if valueType == str:
            return value
        elif valueType == int:
            return int(value)
        elif valueType == float:
            return float(value)
        elif valueType in ((int, float), (float, int)):
            try:
                valInt = int(value)
            except ValueError:
                valInt = None
            try:
                valFloat = float(value)
            except ValueError:
                valFloat = None
            if valInt is None and valFloat is not None:
                return valFloat
            elif valInt is not None and valFloat is None:
                return valInt
            elif valInt is not None and valFloat is not None:
                if abs(valInt - valFloat) < 0.0001:
                    return valInt
                else:
                    return valFloat
        else:
            log.debug("valueType: %r, value: %r", valueType, value)
            raise ValueError(f"Can't get value '{ctrl.Name}' from control'")

    def Validate(self, win):
        ctrl:wx.TextCtrl = self.GetWindow()
        name:str = ctrl.Name
        # log.debug("Validate %r for %s", win, name)
        info = self.fontInfo
        if info:
            if hasattr(info, name):
                try:
                    value = self._getValueFromControl()
                except ValueError:
                    log.debug("ValueError during Validate for %s", name)
                    return False
                if not value:
                    return True
                result = validateFontInfoVersion3ValueForAttribute(name, value)
                if not result:
                    log.debug("Validate for for %s returned %r", name, result)
                return result
            else:
                log.debug("name not found in fontInfo during Validate for %s", name)
        else:
            log.debug("No fontInfo during Validate for %s", name)
        return True

    def TransferToWindow(self):
        ctrl:wx.TextCtrl = self.GetWindow()
        name:str = ctrl.Name
        info = self.fontInfo
        if info and hasattr(info, name):
            value = getattr(info, name)
            if value is None:
                ctrl.Value = wx.EmptyString
            elif isinstance(value, str):
                ctrl.Value = value
            else:
                try:
                    ctrl.Value = str(value)
                except ValueError:
                    return False
        return True
        # log.debug("TransferToWindow: no fontInfo")
        # return False

    def TransferFromWindow(self):
        ctrl:wx.TextCtrl = self.GetWindow()
        name:str = ctrl.Name
        info = self.fontInfo
        if info and hasattr(info, name):
            try:
                setattr(info, name, self._getValueFromControl())
                return True
            except ValueError:
                log.debug("ValueError during TransferFromWindow for %s", name)
                return False
        return False

    def on_char(self, event):
        key = event.GetKeyCode()
        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return
        if self.valueType == str:
            event.Skip()
            return
        elif (
            self.valueType in (int, float, (int, float), (float, int))
            and chr(key) in digits + "+-."
        ):
            event.Skip()
            return
        if not wx.Validator.IsSilent():
            wx.Bell()
        return


class FontInfoIntlistTextCtrlValidator(FontInfoTextCtrlValidator):
    # def __init__(self, getFontInfo):
    #     super().__init__(getFontInfo)

    def _getValueFromControl(self):
        ctrl:wx.TextCtrl = self.GetWindow()
        name:str = ctrl.Name
        info = self.fontInfo
        if info and hasattr(info, name):
            value = ctrl.Value
            if value == wx.EmptyString:
                return []
            else:
                return [int(v) for v in value.split()]
        raise ValueError(f"Can't get value '{name}' from control'")

    def TransferToWindow(self):
        ctrl:wx.TextCtrl = self.GetWindow()
        name:str = ctrl.Name
        info = self.fontInfo
        if info and hasattr(info, name):
            value = getattr(info, name)
            if value is None:
                ctrl.Value = wx.EmptyString
            elif isinstance(value, (list, tuple)):
                if not value:
                    ctrl.Value = wx.EmptyString
                else:
                    ctrl.Value = " ".join([str(v) for v in value])
            else:
                return False
        return True

    def on_char(self, event):
        key = event.GetKeyCode()
        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return
        if chr(key) in digits + whitespace + "+-":
            event.Skip()
            return
        if not wx.Validator.IsSilent():
            wx.Bell()
        return


class FontInfoPShintCtrlValidator(FontInfoBaseValidator):
    def _getValueFromControl(self):
        ctrl = self.GetWindow()
        value = ctrl.Value
        if value:
            return value

    def TransferToWindow(self):
        ctrl = self.GetWindow()
        name:str = ctrl.Name
        info = self.fontInfo
        if info and hasattr(info, name):
            value = getattr(info, name)
            if value is None:
                ctrl.Value = []
            elif isinstance(value, (list, tuple)):
                ctrl.Value = value
            else:
                return False
        return True

    def TransferFromWindow(self):
        ctrl = self.GetWindow()
        name:str = ctrl.Name
        info = self.fontInfo
        if info and hasattr(info, name):
            oldValue = getattr(info, name)
            newValue = self._getValueFromControl()
            if newValue != oldValue:
                try:
                    setattr(info, name, newValue)
                    return True
                except ValueError:
                    log.debug("ValueError during TransferFromWindow for %s", name)
                    return False
        return False


class FontInfoCheckBoxValidator(FontInfoBaseValidator):
    def __init__(self, getFontInfo):
        super().__init__(getFontInfo)
        self.flagsPattern = re.compile(r"^\w+ \d{1,2}$")

    @property
    def valueType(self):
        if self._valueType is None:
            ctrl = self.GetWindow()
            if ctrl:
                name = ctrl.Name
                if self.flagsPattern.match(name):
                    attribute, __ = name.split(" ", 1)
                else:
                    attribute = name
                self._valueType = fontInfoAttributesVersion3ValueData[attribute]["type"]
        return self._valueType

    def TransferToWindow(self):
        ctrl:wx.CheckBox = self.GetWindow()
        name:str = ctrl.Name
        info = self.fontInfo
        if info:
            if self.flagsPattern.match(name):
                attribute, value = name.split(" ", 1)
                value = int(value)
                if hasattr(info, attribute):
                    # log.debug(
                    #     "FontInfoCheckBoxValidator.TransferToWindow(%r)",
                    #     getattr(info, attribute),
                    # )
                    infoValue = getattr(info, attribute)
                    if infoValue:
                        ctrl.Value = value in infoValue
                    else:
                        ctrl.Value = False
                else:
                    ctrl.Value = False
            else:
                attribute = name
                if hasattr(info, attribute):
                    ctrl.Value = bool(getattr(info, attribute))
                else:
                    ctrl.Value = False
        else:
            ctrl.Value = False
        return True

    def TransferFromWindow(self):
        ctrl = self.GetWindow()
        name = ctrl.Name
        info = self.fontInfo
        if info:
            if self.flagsPattern.match(name):
                attribute, value = name.split(" ", 1)
                value = int(value)
                infoValue = list(getattr(info, attribute))
                if ctrl.Value and value not in infoValue:
                    infoValue.append(value)
                    infoValue.sort()
                elif not ctrl.Value and value in infoValue:
                    infoValue.remove(value)
            else:
                attribute = name
                infoValue = ctrl.Value
            log.debug("TransferFromWindow %r, %r", attribute, infoValue)
            setattr(info, attribute, infoValue)
            return True
        log.debug("ValueError during TransferFromWindow for %s", name)
        return False


class FontInfoBitListValidator(FontInfoBaseValidator):
    def TransferToWindow(self):
        ctrl = self.GetWindow()
        name = ctrl.Name
        info = self.fontInfo
        if info and hasattr(info, name):
            ctrl.Value = getattr(info, name)
        else:
            ctrl.Value = ()
        return True

    def TransferFromWindow(self):
        ctrl = self.GetWindow()
        name = ctrl.Name
        info = self.fontInfo
        if info and hasattr(info, name):
            setattr(info, name, ctrl.Value)
            return True
        log.debug("ValueError during TransferFromWindow for %s", name)
        return False
