# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
import os

from qtpy.QtDesigner import QDesignerCustomWidgetInterface

import bec_widgets
from bec_widgets.utils.bec_designer import designer_material_icon
from bec_widgets.widgets.control.device_input.device_combobox.device_combobox import DeviceComboBox

DOM_XML = """
<ui language='c++'>
    <widget class='DeviceComboBox' name='device_combobox'>
    </widget>
</ui>
"""

MODULE_PATH = os.path.dirname(bec_widgets.__file__)


class DeviceComboBoxPlugin(QDesignerCustomWidgetInterface):  # pragma: no cover
    def __init__(self):
        super().__init__()
        self._form_editor = None

    def createWidget(self, parent):
        t = DeviceComboBox(parent)
        return t

    def domXml(self):
        return DOM_XML

    def group(self):
        return "BEC Input Widgets"

    def icon(self):
        return designer_material_icon(DeviceComboBox.ICON_NAME)

    def includeFile(self):
        return "device_combobox"

    def initialize(self, form_editor):
        self._form_editor = form_editor

    def isContainer(self):
        return False

    def isInitialized(self):
        return self._form_editor is not None

    def name(self):
        return "DeviceComboBox"

    def toolTip(self):
        return "Device ComboBox Example for BEC Widgets"

    def whatsThis(self):
        return self.toolTip()
