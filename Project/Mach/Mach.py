# PyQT5 imports
from PyQt5 import QtWidgets, Qt, QtCore, QtGui
from PyQt5.QtGui import QOpenGLContext, QSurfaceFormat, QWindow
from PyQt5.QtCore import QTimer, QTime

# PyOpenGL imports
from OpenGL.GL import *
from OpenGL.GLUT import *

# Mach imports
from Mach.Shader import *
from Mach.Attribute import *
from Mach.Matrix import *
from Mach.Rendered import Texture
import Mach.Delay as md

import time
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        base_path = os.path.join(base_path, "resources")
    except Exception:
        base_path = os.path.abspath("./resources")

    return os.path.join(base_path, relative_path)

class Geometry:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __repr__(self):
        return str((self.x, self.y, self.width, self.height))

class GlQWindow(QWindow):

    keysHeld = [] # A list of keys that are currently being pressed

    def __init__(self, format = None):
        super().__init__()

        # Initialize the delay events
        md.init()

        # Some weird opengl bullshit that makes this whole thing work
        format = QSurfaceFormat()
        format.setVersion(4, 4)
        format.setProfile(QSurfaceFormat.CoreProfile)
        format.setStereo(False)
        format.setSwapBehavior(QSurfaceFormat.DoubleBuffer)
        format.setDepthBufferSize(24)
        self.setSurfaceType(QWindow.OpenGLSurface)
        self.context = QOpenGLContext()
        self.context.setFormat(format)

        if not self.context.create():
            raise Exception('self.context.create() failed')
        self.create()

        # Make the context current
        self.makeCurrent()

        # Start a timer to keep track of time since the beginning of this program
        self.qtime = QTime()
        self.qtime.start()

        self.start()
        self.started = False # Don't actually start rendering until the expose event is called

        # Set for sixty frames per second
        self.FPS = 60

        self.timer = QTimer()

        self.width = 0
        self.height = 0

    # Event handling... I think
    def exposeEvent(self, event):
        event.accept()
        if self.isExposed() and self.isVisible():
            if not self.started:
                self.started = True

                # Start the update thread (Easily done using a QTimer)
                self.timer.timeout.connect(self.update)
                self.timer.start(1 / self.FPS * 1000) # Start the timer to go as fast as possible, managing framerate will be done in the function itself

            self.windowSizeChanged()
            self.timer.start(1 / self.FPS * 1000)

        else:
            self.timer.stop()

    # Make the opengl context held in this window current
    def makeCurrent(self):
        self.context.makeCurrent(self)

        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)
        glDepthFunc(GL_LEQUAL)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Use our double buffer system
    def swapBuffers(self):
        self.context.swapBuffers(self)

    # Called whenever the window size is changed (or some other window event at that)
    def windowSizeChanged(self):
        self.makeCurrent()
        timeSinceStart = self.qtime.elapsed() / 1000
        geom = self.getGeometry()

        self.width = geom.width
        self.height = geom.height

        self.windowResized(self.width, self.height)
        self.swapBuffers()

    # Window resize function that could be overidden by the user
    def windowResized(self, width, height):
        self.draw()

    # Update the screen
    def update(self):
        try:
            timeSinceStart = self.qtime.elapsed() / 1000

            # Handle key events first
            self.keyHeldDown(self.keysHeld)

            self.makeCurrent()
            self.draw()
            self.swapBuffers()

        except KeyboardInterrupt:
            print("\nKeyboard Interrupt")
            self.timer.stop()
            sys.exit(0)

    def keyPressEvent(self, event):
        if not event.isAutoRepeat():
            key = event.key()
            if not key in self.keysHeld: # Sometimes windows likes to add in multiple keys anyway
                self.keysHeld.append(key)
                self.keyPress(key)

    # Called once every time a key is pressed, for the user to override
    def keyPress(self, key):
        pass

    # Called once every update cycle for each key that is being held down, for the user to override
    def keyHeldDown(self, keysHeld):
        pass

    def keyReleaseEvent(self, event):
        if not event.isAutoRepeat():
            key = event.key()
            self.keysHeld.remove(key)
            self.keyRelease(key)

    # Called once a key is released, for the user to override
    def keyRelease(self, key):
        pass

    def bind(self):
        geom = self.getGeometry()
        width = geom.width
        height = geom.height

        # Unbind any frame buffers
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        if sys.platform == 'win32':
            glViewport(0, 0, width + 8, height + 8)
        elif sys.platform == 'darwin':
            glViewport(0, 0, width, height)
        elif sys.platform == 'linux':
            glViewport(0, 0, width, height)

        # Unbind any depth buffers
        glBindRenderbuffer(GL_RENDERBUFFER, 0)

    def getGeometry(self):
        geom = self.geometry()
        pgeom = self.parent().geometry()
        if sys.platform == 'win32':
            return Geometry(pgeom.x() - 8, pgeom.y() - 31, geom.width(), geom.height())
        elif sys.platform == 'darwin':
            return Geometry(pgeom.x(), pgeom.y(), geom.width(), geom.height())
        elif sys.platform == 'linux':
            return 'idk'

    # Called when the window is closed
    def close(self):
        md.close()
