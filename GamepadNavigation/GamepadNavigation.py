# -*- coding: utf-8 -*-
"""Gamepad Navigation

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
import math

from GamepadNavigation.GamepadBridge import GamepadBridge
from GamepadNavigation.GamepadMappingDialog import GamepadMappingDialog

from qgis.core import Qgis, QgsApplication, QgsProject, QgsRectangle, QgsVector
from qgis.gui import QgsMessageBar, QgsMessageBarItem
from qgis._3d import Qgs3DMapScene, QgsCameraController

from qgis.PyQt.QtCore import pyqtSlot, pyqtProperty, pyqtSignal, Qt, QObject, QUrl, QTimer
from qgis.PyQt.QtWidgets import QWidget, QPushButton
from qgis.PyQt.QtGui import QIcon

from PyQt5.QtQuickWidgets import QQuickWidget

VERSION = '0.9'

class GamepadQuickWidget(QQuickWidget):

    mouseClicked = pyqtSignal()
    
    def __init__(self, parent: QWidget = None):
        super(GamepadQuickWidget, self).__init__(parent)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton or event.button() == Qt.LeftButton:
            self.mouseClicked.emit()

class GamepadNavigationPlugin:

    missing_mapping_warning_shown = False
    iface = None
    project = None
    mapping_dialog = None
    timer = QTimer()
    timer_canvas_type = ''
    timer_canvas = None

    def __init__(self, iface):
        super().__init__()
        self.project = QgsProject.instance()
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

    def initGui(self):
        self.mapping_dialog = GamepadMappingDialog(self.iface)

        self.gamepad_bridge = GamepadBridge(self.iface)
        self.gamepad_bridge.deviceIdChanged.connect(self.deviceChanged)
        self.gamepad_bridge.buttonPressed.connect(self.buttonPressed)
        self.gamepad_bridge.axisLeftChanged.connect(self.updateNavigation)
        self.gamepad_bridge.axisRightChanged.connect(self.updateNavigation)
        
        self.widget = GamepadQuickWidget()
        self.widget.rootContext().setContextProperty("gamepadBridge", self.gamepad_bridge)
        self.widget.rootContext().setContextProperty("imagesPath", os.path.join(self.plugin_dir, './images/'))
        self.widget.setSource(QUrl.fromLocalFile(os.path.join(self.plugin_dir, './qml/GamepadWidget.qml')))
        self.widget.setResizeMode(QQuickWidget.SizeRootObjectToView)
        self.iface.statusBarIface().addPermanentWidget(self.widget)
        
        self.widget.mouseClicked.connect(self.toggleMappingDialog)
        self.timer.timeout.connect(self.navigationTimeout)

    def unload(self):
        self.mapping_dialog
        self.timer.timeout.disconnect()
        self.iface.statusBarIface().removeWidget(self.widget)
        self.widget.rootContext().setContextProperty("gamepadBridge", None)
        self.widget.deleteLater()
        self.gamepad_bridge.deleteLater()

    def fetchCanvas(self):
        (canvas_string, found) = self.project.readEntry('GamepadNavigation', 'canvas', '2d:theMapCanvas')
        if not canvas_string == '':
            canvas_type = canvas_string[0:canvas_string.find(':')]
            canvas_name = canvas_string[canvas_string.find(':') + 1:]
        else:
            canvas_type = '2d'
            canvas_name = 'theMapCanvas'
        
        canvas = None
        if canvas_type == '2d':
            for mapCanvas in self.iface.mapCanvases():
                if mapCanvas.objectName() == canvas_name:
                    canvas = mapCanvas
                    break
        elif canvas_type == '3d':
            for scene in Qgs3DMapScene.openScenes().items():
                if scene[0] == canvas_name:
                    canvas = scene[1]
                    break
        if canvas:
            return (canvas_type, canvas_name, canvas)
        else:
            return ('', '', None)

    def deviceChanged(self):
        # stop any ongoing navigation to avoid infinite movement on gamepad disconnect
        self.timer.stop()

    def buttonPressed(self, button: str):
        if self.mapping_dialog.isVisible():
            self.mapping_dialog.setButton(button)
            return

        (canvas_type, canvas_name, canvas) = self.fetchCanvas()
        (action_string, found) = self.project.readEntry('GamepadNavigation', button, '')
        if found:
            try:
                action_type = action_string[0:action_string.find(':')]
                action_details = action_string[action_string.find(':') +1:]
                if action_type == 'bookmark':
                    bookmark = self.project.bookmarkManager().bookmarkById(action_details)
                    if not bookmark:
                            bookmark = QgsApplication.instance().bookmarkManager().bookmarkById(action_details)
                    if bookmark:
                            if canvas_type == '2d':
                                canvas.setExtent(bookmark.extent())
                                canvas.refresh()
                            elif canvas_type == '3d':
                                canvas.setViewFrom2DExtent(bookmark.extent())
                elif action_type == 'map_theme':
                    if not self.project.mapThemeCollection().hasMapTheme(action_details):
                        return;
                    if canvas_type == '2d' and canvas_name != 'theMapCanvas':
                        canvas.setTheme(action_details)
                    elif canvas_type == '3d':
                        canvas.mapSettings().setTerrainMapTheme(action_details)
                    else:
                        root = self.project.layerTreeRoot()
                        model = self.iface.layerTreeView().layerTreeModel()
                        self.project.mapThemeCollection().applyTheme(action_details, root, model)
                return
            except:
                return

        def assignAction():
            self.iface.messageBar().popWidget(widget)
            self.mapping_dialog.updateMapCanvases()
            self.mapping_dialog.show()

        if not self.missing_mapping_warning_shown:
            widget = self.iface.messageBar().createMessage("Action Missing", "The gamepad button has no assigned action in this project yet")
            button = QPushButton(widget)
            button.setText("Assign Action")
            button.pressed.connect(assignAction)
            widget.layout().addWidget(button)
            self.iface.messageBar().pushWidget(widget, Qgis.MessageLevel.Info)
            # avoid spamming the message, just show once
            self.missing_mapping_warning_shown = True

    def toggleMappingDialog(self):
        self.mapping_dialog.updateMapCanvases()
        self.mapping_dialog.show()

    def updateNavigation(self):
        (self.timer_canvas_type, canvas_name, self.timer_canvas) = self.fetchCanvas()
        if not self.timer_canvas:
            return
        
        axis_max = max(abs(self.gamepad_bridge.axisLeftX), abs(self.gamepad_bridge.axisLeftY), abs(self.gamepad_bridge.axisRightX), abs(self.gamepad_bridge.axisRightY))
        if axis_max > 0.12:
            if not self.timer.isActive():
                self.gamepad_bridge.axisLeftChanged.disconnect(self.updateNavigation)
                self.gamepad_bridge.axisRightChanged.disconnect(self.updateNavigation)
                if self.timer_canvas_type == '2d':
                    self.timer_canvas.stopRendering()
                    self.timer_canvas.freeze(True)
                self.timer.start(50)
                self.navigationTimeout()

    def navigationTimeout(self):
        axis_max = max(abs(self.gamepad_bridge.axisLeftX), abs(self.gamepad_bridge.axisLeftY), abs(self.gamepad_bridge.axisRightX), abs(self.gamepad_bridge.axisRightY))
        if axis_max <= 0.12:
            self.gamepad_bridge.axisLeftChanged.connect(self.updateNavigation)
            self.gamepad_bridge.axisRightChanged.connect(self.updateNavigation)
            self.timer.stop()
            if self.timer_canvas_type == '2d':
                self.timer_canvas.freeze(False)
                self.timer_canvas.refresh()
            return

        try:
            if self.timer_canvas_type == '2d':
                map_units_per_pixel = self.timer_canvas.mapSettings().mapUnitsPerPixel()        
                move_x = 0.0
                move_y = 0.0
                if abs(self.gamepad_bridge.axisLeftX) > 0.1:
                    move_x = map_units_per_pixel * 50 * self.gamepad_bridge.axisLeftX
                if abs(self.gamepad_bridge.axisLeftY) > 0.1:
                    move_y = map_units_per_pixel * -50 * self.gamepad_bridge.axisLeftY
                
                if move_x != 0.0 or move_y != 0.0:
                    rad = math.radians(self.timer_canvas.rotation())
                    center = self.timer_canvas.mapSettings().extent().center()
                    center.setX(center.x() + (move_x * math.cos(rad) - move_y * math.sin(rad)))
                    center.setY(center.y() + (move_y * math.cos(rad) + move_x * math.sin(rad)))
                    self.timer_canvas.setCenter(center)
                
                if abs(self.gamepad_bridge.axisRightY) > 0.2:
                    extent = self.timer_canvas.mapSettings().extent()
                    extent.scale(1 + self.gamepad_bridge.axisRightY * 0.25)
                    self.timer_canvas.setExtent(extent)
                
                if abs(self.gamepad_bridge.axisRightX) > 0.5:
                    rotation = self.timer_canvas.mapSettings().rotation() + 5 * self.gamepad_bridge.axisRightX
                    if rotation > 360:
                        rotation = -360 + (rotation - 360)
                    elif rotation < -360:
                         rotation = 360 + (rotation + 360)
                    self.timer_canvas.setRotation(rotation)
            elif self.timer_canvas_type == '3d':
                move_x = 0.0
                move_y = 0.0
                if abs(self.gamepad_bridge.axisLeftY) > 0.1:
                    move_x = -10 * self.gamepad_bridge.axisLeftY
                if abs(self.gamepad_bridge.axisLeftX) > 0.1:
                    move_y = -10 * self.gamepad_bridge.axisLeftX
                
                if move_x != 0.0 or move_y != 0.0:
                    movement_speed = self.timer_canvas.cameraController().cameraMovementSpeed()
                    self.timer_canvas.cameraController().walkView(move_x * movement_speed, move_y * movement_speed, 0)
                
                pitch = 0.0
                yaw = 0.0
                if abs(self.gamepad_bridge.axisRightY) > 0.2:
                    pitch = -5 * self.gamepad_bridge.axisRightY
                if abs(self.gamepad_bridge.axisRightX) > 0.2:
                    yaw = -5 * self.gamepad_bridge.axisRightX
                self.timer_canvas.cameraController().rotateCamera(pitch, yaw)
        except:
            # catch scenarios such as closing a canvas while navigating 
            self.timer.stop()
