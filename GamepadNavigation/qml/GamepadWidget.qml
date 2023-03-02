import QtQuick 2.14
import QtQuick.Controls 2.14
import QtGamepad 1.14

Item {
  width: 64
  
  function updateNavigation() {
    var axisLeftMax = Math.max(Math.abs(gamepad.axisLeftX), Math.abs(gamepad.axisLeftY))
    var axisRightMax = Math.max(Math.abs(gamepad.axisRightX), Math.abs(gamepad.axisRightY))
    if (axisLeftMax > 0.1 || axisRightMax > 0.1) {
      timer.running = true
    } else {
      if (timer.running) {
        timer.running = false
        gamepadBridge.refresh()
      }
    }
  }
  
  Gamepad {
    id: gamepad
    
    deviceId: GamepadManager.connectedGamepads.length > 0 ? GamepadManager.connectedGamepads[0] : 0
    onDeviceIdChanged: gamepadBridge.deviceId = deviceId
    
    onAxisLeftXChanged: gamepadBridge.axisLeftX = axisLeftX
    onAxisLeftYChanged: gamepadBridge.axisLeftY = axisLeftY
    onAxisRightXChanged: gamepadBridge.axisRightX = axisRightX
    onAxisRightYChanged: gamepadBridge.axisRightY = axisRightY
    onButtonL1Changed: gamepadBridge.buttonL1 = buttonL1
    onButtonL2Changed: gamepadBridge.buttonL2 = buttonL2 > 0.5
    onButtonL3Changed: gamepadBridge.buttonL3 = buttonL3
    onButtonR1Changed: gamepadBridge.buttonR1 = buttonR1
    onButtonR2Changed: gamepadBridge.buttonR2 = buttonR2 > 0.5
    onButtonR3Changed: gamepadBridge.buttonR3 = buttonR3
    onButtonAChanged: gamepadBridge.buttonA = buttonA
    onButtonBChanged: gamepadBridge.buttonB = buttonB
    onButtonXChanged: gamepadBridge.buttonX = buttonX
    onButtonYChanged: gamepadBridge.buttonY = buttonY
    onButtonUpChanged: gamepadBridge.buttonUp = buttonUp
    onButtonDownChanged: gamepadBridge.buttonDown = buttonDown
    onButtonLeftChanged: gamepadBridge.buttonLeft = buttonLeft
    onButtonRightChanged: gamepadBridge.buttonRight = buttonRight
  }

  SystemPalette {
    id: palette
    colorGroup: SystemPalette.Active
  }

  Rectangle {
    anchors.fill: parent
    color: palette.base
    
    Image {
      anchors.fill: parent
      width: parent.height - 4
      height: parent.height - 4
      source: gamepad.deviceId != 0 
              ? imagesPath + 'gamepad_on.svg'
              : imagesPath + 'gamepad_off.svg'
      fillMode: Image.PreserveAspectFit
    }
  }
}
