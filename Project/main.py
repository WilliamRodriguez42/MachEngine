from Mach.Shader import *
from Mach.Mach import *
from Mach.Rendered import Texture, DepthTexture
from Mach.Camera import Camera
from Mach.UniformBlock import UniformBlock
from Mach.Struct import Struct
from Mach.Matrix import *
from Mach.transformations import clip_matrix
from Mach.Audio import *
from Mach.Camera import *
import Mach.TextureAtlas as ta

import Mega.PlayerManager as pm
import Mega.HitAndHurt as hnh
import Mega.RenderObject as ren
import Mega.MegaObject as mo
from Mega.Scene import Scene

from PyQt5 import Qt, QtGui, QtCore
import numpy as np

import sys

pixels_in_height = 100
aspect_ratio = 16/9

class Game(GlQWindow):
    captureMouse = False
    mouseCaptured = False

    def start(self):
        hnh.init()
        ren.init()
        mo.init()


    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


    # Called whenever the window is resized
    def windowResized(self, width, height):
        self.bind()

    # Key handling
    def keyPress(self, key):
        if key == QtCore.Qt.Key_Escape:
            self.mouseCaptured = False
            self.setCursor(Qt.Qt.ArrowCursor)

    # Mouse events
    def mousePressEvent(self, event):
        x = event.x()
        y = event.y()

        # Capture the mouse
        if self.captureMouse and not self.mouseCaptured:
            self.setCursor(Qt.Qt.BlankCursor)

            cursor = QtGui.QCursor()
            cursor.setPos(-1, -1)

            geom = self.getGeometry()
            originX = geom.width / 2
            originY = geom.height / 2
            cursor.setPos(geom.x + originX, geom.y + originY)

            self.mouseCaptured = True

    def mouseMoveEvent(self, event):
        x = event.x()
        y = event.y()

        if self.mouseCaptured:
            geom = self.getGeometry()

            originX = geom.width / 2
            originY = geom.height / 2

            deltaX = x - originX
            deltaY = y - originY

            cursor = QtGui.QCursor()
            cursor.setPos(geom.x + originX, geom.y + originY)

if __name__ == "__main__":
    # create the QT App and window
    width, height = 1066, 600

    app = Qt.QApplication([])
    glQWindow = Game()

    glQWindowWidget = Qt.QWidget.createWindowContainer(glQWindow, None, Qt.Qt.Widget)
    glQWindowWidget.show()
    glQWindowWidget.resize(width, height)
    app.exec_()
