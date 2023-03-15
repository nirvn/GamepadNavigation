# Gamepad Navigation, a QGIS plugin

This QGIS plugin enables users to interact with their QGIS 2D and 3D map
canvases using gamepad controllers.

Current functionality includes:
- zooming, panning, and rotating 2D map canvases
- navigating 3D map canvases
- switching map themes
- going to saved user and project bookmarks

## Plugin dependencies

### Window

The official QGIS installer already ships with all of the dependencies
needed to run the plugin, enjoy!

### Linux

You will need to insure that a few Qt-related packages are installed
on your system the plugin to run.

- On Ubuntu, install `python3-pyqt5-qtquick` and `qml-module-gamepad`
- On Fedora, install `python3-qt5` and `qt5-qtgamepad` 
