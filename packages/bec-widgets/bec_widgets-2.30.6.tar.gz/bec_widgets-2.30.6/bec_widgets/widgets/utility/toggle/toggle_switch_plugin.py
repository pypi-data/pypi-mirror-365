# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
import os

from qtpy.QtDesigner import QDesignerCustomWidgetInterface

import bec_widgets
from bec_widgets.utils.bec_designer import designer_material_icon
from bec_widgets.widgets.utility.toggle.toggle import ToggleSwitch

DOM_XML = """
<ui language='c++'>
    <widget class='ToggleSwitch' name='toggle_switch'>
    </widget>
</ui>
"""

MODULE_PATH = os.path.dirname(bec_widgets.__file__)


class ToggleSwitchPlugin(QDesignerCustomWidgetInterface):  # pragma: no cover
    def __init__(self):
        super().__init__()
        self._form_editor = None

    def createWidget(self, parent):
        t = ToggleSwitch(parent)
        return t

    def domXml(self):
        return DOM_XML

    def group(self):
        return "BEC Utils"

    def icon(self):
        return designer_material_icon(ToggleSwitch.ICON_NAME)

    def includeFile(self):
        return "toggle_switch"

    def initialize(self, form_editor):
        self._form_editor = form_editor

    def isContainer(self):
        return False

    def isInitialized(self):
        return self._form_editor is not None

    def name(self):
        return "ToggleSwitch"

    def toolTip(self):
        return "ToggleSwitch"

    def whatsThis(self):
        return self.toolTip()
