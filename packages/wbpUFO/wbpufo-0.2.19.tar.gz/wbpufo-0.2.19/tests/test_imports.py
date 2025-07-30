"""
Very simple test, just check that all modules are importable
"""
import sys
from types import ModuleType

import pytest
from wbBase.application import App
from wbBase.applicationInfo import ApplicationInfo, PluginInfo

appinfo = ApplicationInfo(Plugins=[PluginInfo(Name="ufo", Installation="default")])


def test_plugin():
    app = App(test=True, info=appinfo)
    assert "ufo" in app.pluginManager
    app.Destroy()


def test_config():
    from wbpUFO import config

    assert isinstance(config, ModuleType)


def test_document():
    from wbpUFO import document

    assert isinstance(document, ModuleType)


def test_template():
    from wbpUFO import template

    assert isinstance(template, ModuleType)


def test_view_glyph():
    from wbpUFO.view import glyph

    assert isinstance(glyph, ModuleType)


if __name__ == "__main__":
    pytest.main(sys.argv)
