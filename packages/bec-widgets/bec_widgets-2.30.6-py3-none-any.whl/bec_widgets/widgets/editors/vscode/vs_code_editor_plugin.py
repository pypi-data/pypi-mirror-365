# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
import os

from qtpy.QtDesigner import QDesignerCustomWidgetInterface

import bec_widgets
from bec_widgets.utils.bec_designer import designer_material_icon
from bec_widgets.widgets.editors.vscode.vscode import VSCodeEditor

DOM_XML = """
<ui language='c++'>
    <widget class='VSCodeEditor' name='vs_code_editor'>
    </widget>
</ui>
"""

MODULE_PATH = os.path.dirname(bec_widgets.__file__)


class VSCodeEditorPlugin(QDesignerCustomWidgetInterface):  # pragma: no cover
    def __init__(self):
        super().__init__()
        self._form_editor = None

    def createWidget(self, parent):
        t = VSCodeEditor(parent)
        return t

    def domXml(self):
        return DOM_XML

    def group(self):
        return "BEC Developer"

    def icon(self):
        return designer_material_icon(VSCodeEditor.ICON_NAME)

    def includeFile(self):
        return "vs_code_editor"

    def initialize(self, form_editor):
        self._form_editor = form_editor

    def isContainer(self):
        return False

    def isInitialized(self):
        return self._form_editor is not None

    def name(self):
        return "VSCodeEditor"

    def toolTip(self):
        return ""

    def whatsThis(self):
        return self.toolTip()
