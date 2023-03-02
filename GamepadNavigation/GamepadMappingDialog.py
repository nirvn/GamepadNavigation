# -*- coding: utf-8 -*-
"""Gamepad Mapping Dialog

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

__author__ = '(C) 2023 by Mathieu Pellerin'
__date__ = '11/02/2023'
__copyright__ = 'Copyright 2023, Mathieu Pellerin'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import os

from qgis.core import QgsApplication, QgsProject, QgsBookmarkManagerModel
from qgis._3d import Qgs3DMapScene

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QMainWindow, QWidget
from qgis.PyQt.uic import loadUiType

GamepadMappingDialogUi, _ = loadUiType(
    os.path.join(os.path.dirname(__file__), "ui/gamepad_mapping_dialog.ui")
)


class GamepadMappingDialog(QDialog, GamepadMappingDialogUi):

    iface = None
    project = None
    bookmark_model = None

    def __init__(self, iface, parent: QWidget = None):
        super(GamepadMappingDialog, self).__init__(parent=parent)
        self.setupUi(self)
        
        self.iface = iface
        self.project = QgsProject.instance()
        self.bookmark_model = QgsBookmarkManagerModel(QgsApplication.instance().bookmarkManager(), self.project.bookmarkManager())
        
        self.buttonBox.button(QDialogButtonBox.Close).clicked.connect(lambda:self.hide())
        self.assignActionButton.released.connect(self.assignAction)
        self.clearActionButton.released.connect(self.clearAction)
        
        self.mapCanvasCombobox.currentIndexChanged.connect(self.mapCanvasChanged)
        
        self.buttonCombobox.addItem('Button Left #1', 'buttonL1')
        self.buttonCombobox.addItem('Button Left #3', 'buttonL3')
        self.buttonCombobox.addItem('Button Right #1', 'buttonR1')
        self.buttonCombobox.addItem('Button Right #3', 'buttonR3')
        self.buttonCombobox.addItem('Button A / X', 'buttonA')
        self.buttonCombobox.addItem('Button B / Circle', 'buttonB')
        self.buttonCombobox.addItem('Button X / Square', 'buttonX')
        self.buttonCombobox.addItem('Button Y / Triangle', 'buttonY')
        self.buttonCombobox.addItem('Button Up', 'buttonUp')
        self.buttonCombobox.addItem('Button Down', 'buttonDown')
        self.buttonCombobox.addItem('Button Left', 'buttonLeft')
        self.buttonCombobox.addItem('Button Right', 'buttonRight')
        self.buttonCombobox.currentIndexChanged.connect(self.buttonChanged)
        
        self.actionTypeCombobox.addItem('Go To Bookmark', 'bookmark')
        self.actionTypeCombobox.addItem('Switch Map Theme', 'map_theme')
        self.actionTypeCombobox.currentIndexChanged.connect(self.actionTypeChanged)
        
        self.bookmarkActionCombobox.setModel(self.bookmark_model)
        
        self.setButton('buttonL1')
        self.setActionType('bookmark')

    def assignAction(self):
        action_string = self.actionTypeCombobox.currentData()
        if action_string == 'bookmark':
            action_string = 'bookmark:{}'.format(self.bookmarkActionCombobox.currentData(QgsBookmarkManagerModel.RoleId))
        elif action_string == 'map_theme':
            action_string = 'map_theme:{}'.format(self.mapThemeActionCombobox.currentText())
        else:
            return

        self.project.writeEntry('GamepadNavigation', self.buttonCombobox.currentData(), action_string)
        self.updateCurrentAction()

    def clearAction(self):
        self.project.removeEntry('GamepadNavigation', self.buttonCombobox.currentData())
        self.updateCurrentAction()

    def actionTypeChanged(self):
        self.setActionType(self.actionTypeCombobox.currentData())

    def setActionType(self, action_type: str):
        if action_type == 'bookmark':
            self.bookmarkActionCombobox.setVisible(True)
            self.mapThemeActionCombobox.setVisible(False)
        elif action_type == 'map_theme':
            self.bookmarkActionCombobox.setVisible(False)
            self.mapThemeActionCombobox.clear()
            for map_theme in self.project.mapThemeCollection().mapThemes():
                self.mapThemeActionCombobox.addItem(QgsApplication.instance().getThemeIcon('mLayoutItemMap.svg'), map_theme)
            self.mapThemeActionCombobox.setVisible(True)
        else:
            return

        self.actionTypeCombobox.blockSignals(True)
        self.actionTypeCombobox.setCurrentIndex(self.actionTypeCombobox.findData(action_type))
        self.actionTypeCombobox.blockSignals(False)

    def updateMapCanvases(self):
        self.mapCanvasCombobox.blockSignals(True)
        self.mapCanvasCombobox.clear()
        for mapCanvas in self.iface.mapCanvases():
            canvas_name = self.tr( "Main window map canvas" ) if mapCanvas.objectName() == "theMapCanvas" else mapCanvas.objectName()
            self.mapCanvasCombobox.addItem(QgsApplication.instance().getThemeIcon('mLayoutItemMap.svg'), canvas_name + ' (2D)', '2d:' + mapCanvas.objectName())
        for sceneName in Qgs3DMapScene.openScenes().keys():
            self.mapCanvasCombobox.addItem(QgsApplication.instance().getThemeIcon('mLayoutItem3DMap.svg'), sceneName + ' (2D)', '3d:' + sceneName)
        (canvas_string, found) = self.project.readEntry('GamepadNavigation', 'canvas', '2d:theMapCanvas')
        idx = self.mapCanvasCombobox.findData(canvas_string)
        if idx == -1:
            try: 
                idx = self.mapCanvasCombobox.count()
                canvas_type = canvas_string[0:canvas_string.find(':')]
                canvas_name = canvas_string[canvas_string.find(':') + 1:]
                canvas_icon = QgsApplication.instance().getThemeIcon('mLayoutItemMap.svg')
                if canvas_type == '2d':
                    canvas_name += ' (2D)'
                else:
                    canvas_name += ' (3D)'
                    canvas_icon = QgsApplication.instance().getThemeIcon('mLayoutItem3DMap.svg')
                self.mapCanvasCombobox.addItem(canvas_icon, canvas_name, canvas_string)
            except:
                idx = 0

        self.mapCanvasCombobox.setCurrentIndex(idx)
        self.mapCanvasCombobox.blockSignals(False)

    def mapCanvasChanged(self):
        self.project.writeEntry('GamepadNavigation', 'canvas', self.mapCanvasCombobox.currentData())

    def buttonChanged(self):
        self.setButton(self.buttonCombobox.currentData())

    def setButton(self, button: str):
        idx = self.buttonCombobox.findData(button)
        if idx < 0:
            return

        self.buttonCombobox.blockSignals(True)
        self.buttonCombobox.setCurrentIndex(idx)
        self.buttonCombobox.blockSignals(False)
        
        self.updateCurrentAction()

    def updateCurrentAction(self):
        (action_string, found) = self.project.readEntry('GamepadNavigation', self.buttonCombobox.currentData(), '')
        self.clearActionButton.setEnabled(found)
        if found:
            try:
                action_type = action_string[0:action_string.find(':')]
                action_details = action_string[action_string.find(':') +1:]
                if action_type == 'bookmark':
                    bookmark = self.project.bookmarkManager().bookmarkById(action_details)
                    if not bookmark:
                        bookmark = QgsApplication.instance().bookmarkManager().bookmarkById(action_details)
                    if bookmark:
                        self.currentAction.setText('Go to bookmark \'{}\''.format(bookmark.name()))
                    else:
                        self.currentAction.setText('Error: action bookmark missing')
                elif action_type == 'map_theme':
                    self.currentAction.setText('Set map theme to \'{}\''.format(action_details))
            except:
                self.currentAction.setText('Error: wrong/corrupted action string, please re-assign')
        else:
            self.currentAction.setText('n/a')
