# -*- coding: utf-8 -*-
"""Gamepad Bridge

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
import signal

from qgis.PyQt.QtCore import pyqtSlot, pyqtProperty, pyqtSignal, Qt, QObject

class GamepadBridge(QObject):

    deviceIdChanged = pyqtSignal()
    axisLeftChanged = pyqtSignal()
    axisRightChanged = pyqtSignal()
    buttonL2Changed = pyqtSignal()
    buttonR2Changed = pyqtSignal()
    buttonPressed = pyqtSignal(str)

    _deviceId = 0
    _axisLeftX = 0.0
    _axisLeftY = 0.0
    _axisRightX = 0.0
    _axisRightY = 0.0
    _buttonR1 = False
    _buttonR2 = 0.0
    _buttonR3 = False
    _buttonL1 = False
    _buttonL2 = 0.0
    _buttonL3 = False
    _buttonA = False
    _buttonB = False
    _buttonX = False
    _buttonY = False
    _buttonUp = False
    _buttonDown = False
    _buttonLeft = False
    _buttonRight = False
    _buttonSelect = False
    _buttonStart = False

    def __init__(self, iface, parent: QObject = None):
        super(GamepadBridge, self).__init__(parent)
        self.iface =  iface

    @pyqtProperty(int)
    def deviceId(self):
        return self._deviceId
    @deviceId.setter
    def deviceId(self, value):
        if self._deviceId != value:
            self._deviceId = value
            self.deviceIdChanged.emit()

    @pyqtProperty(float)
    def axisLeftX(self):
        return self._axisLeftX
    @axisLeftX.setter
    def axisLeftX(self, value):
        if self._axisLeftX != value:
            self._axisLeftX = value
            self.axisLeftChanged.emit()

    @pyqtProperty(float)
    def axisLeftY(self):
        return self._axisLeftY
    @axisLeftY.setter
    def axisLeftY(self, value):
        if self._axisLeftY != value:
            self._axisLeftY = value
            self.axisLeftChanged.emit()

    @pyqtProperty(float)
    def axisRightX(self):
        return self._axisRightX
    @axisRightX.setter
    def axisRightX(self, value):
        if self._axisRightX != value:
            self._axisRightX = value
            self.axisRightChanged.emit()

    @pyqtProperty(float)
    def axisRightY(self):
        return self._axisRightY
    @axisRightY.setter
    def axisRightY(self, value):
        if self._axisRightY != value:
            self._axisRightY = value
            self.axisRightChanged.emit()

    @pyqtProperty(bool)
    def buttonR1(self):
        return self._buttonR1
    @buttonR1.setter
    def buttonR1(self, value):
        if self._buttonR1 != value:
            self._buttonR1 = value
            if self._buttonR1:
                self.buttonPressed.emit('buttonR1')
    @pyqtProperty(float)
    def buttonR2(self):
        return self._buttonR2
    @buttonR2.setter
    def buttonR2(self, value):
        if self._buttonR2 != value:
            self._buttonR2 = value
            if self._buttonR2:
                self.buttonR2Changed.emit()
    @pyqtProperty(bool)
    def buttonR3(self):
        return self._buttonR3
    @buttonR3.setter
    def buttonR3(self, value):
        if self._buttonR3 != value:
            self._buttonR3 = value
            if self._buttonR3:
                self.buttonPressed.emit('buttonR3')

    @pyqtProperty(bool)
    def buttonL1(self):
        return self._buttonL1
    @buttonL1.setter
    def buttonL1(self, value):
        if self._buttonL1 != value:
            self._buttonL1 = value
            if self._buttonL1:
                self.buttonPressed.emit('buttonL1')
    @pyqtProperty(float)
    def buttonL2(self):
        return self._buttonL2
    @buttonL2.setter
    def buttonL2(self, value):
        if self._buttonL2 != value:
            self._buttonL2 = value
            if self._buttonL2:
                self.buttonL2Changed.emit()
    @pyqtProperty(bool)
    def buttonL3(self):
        return self._buttonL3
    @buttonL3.setter
    def buttonL3(self, value):
        if self._buttonL3 != value:
            self._buttonL3 = value
            if self._buttonL3:
                self.buttonPressed.emit('buttonL3')

    @pyqtProperty(bool)
    def buttonA(self):
        return self._buttonA
    @buttonA.setter
    def buttonA(self, value):
        if self._buttonA != value:
            self._buttonA = value
            if self._buttonA:
                self.buttonPressed.emit('buttonA')
    @pyqtProperty(bool)
    def buttonB(self):
        return self._buttonB
    @buttonB.setter
    def buttonB(self, value):
        if self._buttonB != value:
            self._buttonB = value
            if self._buttonB:
                self.buttonPressed.emit('buttonB')
    @pyqtProperty(bool)
    def buttonX(self):
        return self._buttonX
    @buttonX.setter
    def buttonX(self, value):
        if self._buttonX != value:
            self._buttonX = value
            if self._buttonX:
                self.buttonPressed.emit('buttonX')
    @pyqtProperty(bool)
    def buttonY(self):
        return self._buttonY
    @buttonY.setter
    def buttonY(self, value):
        if self._buttonY != value:
            self._buttonY = value
            if self._buttonY:
                self.buttonPressed.emit('buttonY')

    @pyqtProperty(bool)
    def buttonUp(self):
        return self._buttonUp
    @buttonUp.setter
    def buttonUp(self, value):
        if self._buttonUp != value:
            self._buttonUp = value
            if self._buttonUp:
                self.buttonPressed.emit('buttonUp')
    @pyqtProperty(bool)
    def buttonDown(self):
        return self._buttonDown
    @buttonDown.setter
    def buttonDown(self, value):
        if self._buttonDown != value:
            self._buttonDown = value
            if self._buttonDown:
                self.buttonPressed.emit('buttonDown')
    @pyqtProperty(bool)
    def buttonLeft(self):
        return self._buttonLeft
    @buttonLeft.setter
    def buttonLeft(self, value):
        if self._buttonLeft != value:
            self._buttonLeft = value
            if self._buttonLeft:
                self.buttonPressed.emit('buttonLeft')
    @pyqtProperty(bool)
    def buttonRight(self):
        return self._buttonRight
    @buttonRight.setter
    def buttonRight(self, value):
        if self._buttonRight != value:
            self._buttonRight = value
            if self._buttonRight:
                self.buttonPressed.emit('buttonRight')

    @pyqtProperty(bool)
    def buttonSelect(self):
        return self._buttonSelect
    @buttonSelect.setter
    def buttonSelect(self, value):
        if self._buttonSelect != value:
            self._buttonSelect = value
            if self._buttonSelect:
                self.buttonPressed.emit('buttonSelect')
    @pyqtProperty(bool)
    def buttonStart(self):
        return self._buttonStart
    @buttonStart.setter
    def buttonStart(self, value):
        if self._buttonStart != value:
            self._buttonStart = value
            if self._buttonStart:
                self.buttonPressed.emit('buttonStart')
