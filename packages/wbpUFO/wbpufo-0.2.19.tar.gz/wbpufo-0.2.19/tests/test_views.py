import sys

import pytest
from wbBase.application import App
from wbBase.applicationInfo import ApplicationInfo, PluginInfo
from wbBase.document import DOC_NEW

from wbpUFO.template import UfoTemplate
from wbpUFO.view.font import UfoFontView
from wbpUFO.view.glyph import UfoGlyphView
from wbpUFO.view.fontinfo import UfoFontInfoView

appinfo = ApplicationInfo(Plugins=[PluginInfo(Name="ufo", Installation="default")])


def test_UfoFontView():
    app = App(debug=0, test=True, info=appinfo)
    template = app.documentManager.FindTemplateByType(UfoTemplate)
    document = template.CreateDocument("", DOC_NEW)
    document.OnNewDocument()
    assert len(document.views) == 1
    assert isinstance(document.views[0], UfoFontView)
    app.Destroy()


def test_UfoGlyphView():
    app = App(debug=0, test=True, info=appinfo)
    template = app.documentManager.FindTemplateByType(UfoTemplate)
    document = template.CreateDocument("", DOC_NEW)
    document.OnNewDocument()
    glyphView = template.CreateView(document, 0, UfoGlyphView)
    assert isinstance(glyphView, UfoGlyphView)
    assert len(document.views) == 2
    app.Destroy()


def test_UfoFontInfoView():
    app = App(debug=0, test=True, info=appinfo)
    template = app.documentManager.FindTemplateByType(UfoTemplate)
    document = template.CreateDocument("", DOC_NEW)
    document.OnNewDocument()
    glyphView = template.CreateView(document, 0, UfoFontInfoView)
    assert isinstance(glyphView, UfoFontInfoView)
    assert len(document.views) == 2
    app.Destroy()


if __name__ == "__main__":
    pytest.main(sys.argv)
