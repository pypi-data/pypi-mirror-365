import sys

import pytest
from wbBase.application import App
from wbBase.applicationInfo import ApplicationInfo, PluginInfo

from wbpUFO.template import UfoTemplate, VFBTemplate, GlyphsTemplate

appinfo = ApplicationInfo(Plugins=[PluginInfo(Name="ufo", Installation="default")])


def test_UfoTemplate():
    app = App(debug=0, test=True, info=appinfo)
    assert any(isinstance(t, UfoTemplate) for t in app.documentManager.templates)
    assert any(isinstance(t, UfoTemplate) for t in app.documentManager.visibleTemplates)
    assert isinstance(
        app.documentManager.FindTemplateByType(UfoTemplate),
        UfoTemplate,
    )
    assert isinstance(app.documentManager.FindTemplateForPath("test.ufo"), UfoTemplate)
    assert isinstance(app.documentManager.FindTemplateForPath("test.ufoz"), UfoTemplate)
    app.Destroy()


def test_VFBTemplate():
    app = App(debug=0, test=True, info=appinfo)
    assert any(isinstance(t, VFBTemplate) for t in app.documentManager.templates)
    assert any(isinstance(t, VFBTemplate) for t in app.documentManager.visibleTemplates)
    assert isinstance(
        app.documentManager.FindTemplateByType(VFBTemplate),
        VFBTemplate,
    )
    assert isinstance(app.documentManager.FindTemplateForPath("test.vfb"), VFBTemplate)
    app.Destroy()


def test_GlyphsTemplate():
    app = App(debug=0, test=True, info=appinfo)
    assert any(isinstance(t, GlyphsTemplate) for t in app.documentManager.templates)
    assert any(isinstance(t, GlyphsTemplate) for t in app.documentManager.visibleTemplates)
    assert isinstance(
        app.documentManager.FindTemplateByType(GlyphsTemplate),
        GlyphsTemplate,
    )
    assert isinstance(app.documentManager.FindTemplateForPath("test.glyphs"), GlyphsTemplate)
    app.Destroy()


if __name__ == "__main__":
    pytest.main(sys.argv)
