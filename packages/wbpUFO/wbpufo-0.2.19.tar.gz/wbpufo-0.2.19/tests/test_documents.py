import sys

import pytest
from wbBase.application import App
from wbBase.applicationInfo import ApplicationInfo, PluginInfo
from wbBase.document import DOC_NEW

from wbpUFO.template import UfoTemplate
from wbpUFO.document import UfoDocument

appinfo = ApplicationInfo(Plugins=[PluginInfo(Name="ufo", Installation="default")])


def test_UfoDocument():
    app = App(debug=0, test=True, info=appinfo)
    template = app.documentManager.FindTemplateByType(UfoTemplate)
    document = template.CreateDocument("", DOC_NEW)
    assert isinstance(document, UfoDocument)
    assert document in app.documentManager.documents
    app.Destroy()

if __name__ == "__main__":
    pytest.main(sys.argv)
