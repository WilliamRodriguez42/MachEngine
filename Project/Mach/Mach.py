# PyQT5 imports
from PyQt5 import Qt
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QOpenGLContext, QSurfaceFormat, QWindow
from PyQt5.QtCore import QTimer

# PyOpenGL imports
from OpenGL.GL import *
from OpenGL.GLUT import *

# Mach imports
import mach
# from Mach.Shader import *
# from Mach.Attribute import *
# from Mach.Matrix import *
# from Mach.Rendered import Texture

import time
import sys
import os

import threading

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

class Window(QWindow):

	keys_held_down = [] # A list of keys that are currently being pressed

	def __init__(self):
		super().__init__()

		# Some weird opengl stuff that makes this whole thing work
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

		self.event = mach.EventManager()
		self.start()
		self.exposed = threading.Event() # Don't actually start rendering until the expose event is called

		# Default for sixty frames per second
		self.FPS = 60

		self.timer = QTimer()

	def start(self):
		return

	def draw(self):
		return

	def set_FPS(self, FPS):
		self.exposed.wait()
		self.FPS = FPS
		self.timer.start(1 / self.FPS * 1000)

	# Make the opengl context held in this window current
	def makeCurrent(self):
		self.context.makeCurrent(self)

		glEnable(GL_DEPTH_TEST)
		glDepthMask(GL_TRUE)
		glDepthFunc(GL_LEQUAL)

		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

	def clear(self):
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	# Update the screen
	def update(self):
		try:
			self.makeCurrent()
			self.draw()

		except KeyboardInterrupt:
			print("\nKeyboard Interrupt")
			self.timer.stop()
			sys.exit(0)

	# Handle video expose / resize events
	def exposeEvent(self, event):
		event.accept()
		if self.isExposed() and self.isVisible():
			if not self.exposed.is_set():
				self.exposed.set()

				# Start the update thread
				self.timer.timeout.connect(self.update)
				self.timer.start(1 / self.FPS * 1000) # Start the timer to go as fast as possible, managing framerate will be done in the function itself

			self.makeCurrent()
			geom = self.getGeometry()

			self.event.queue_event(mach.Event(
				mach.VIDEORESIZE,
				size = (geom.width, geom.height)
			))

			self.window_resized(geom.width, geom.height)
			self.timer.start(1 / self.FPS * 1000)

	# Called once the mouse is resized, for the user to override
	def window_resized(self, width, height):
		return

	# Automate window close events for pygame style event handling
	def closeEvent(self, event):
		event.ignore() # Ignore the event by default, it is okay to call accept later
		self.event.queue_event(mach.Event(
			mach.QUIT
		))
		self.close_event(event)
		if event.isAccepted():
			self.timer.stop()

	# Called once the user attempts to close the application, for the user to override
	def close_event(self, event):
		return

	# Automates key pressed events for pygame style event handling
	def keyPressEvent(self, event):
		event.accept() # Accept the event by default, it is okay to call ignore later
		if not event.isAutoRepeat():
			key = event.key()
			if not key in self.keys_held_down: # Sometimes windows likes to add in multiple keys anyway
				self.keys_held_down.append(key)
				self.event.queue_event(mach.Event(
					mach.KEYDOWN,
					key
				))
				self.key_pressed(key)

	# Called once every time a key is pressed, for the user to override
	def key_pressed(self, key):
		return

	# Automates key released events for pygame style event handling
	def keyReleaseEvent(self, event):
		event.accept() # Accept the event by default, it is okay to call ignore later
		if not event.isAutoRepeat():
			key = event.key()
			self.keys_held_down.remove(key)
			self.event.queue_event(mach.Event(
				mach.KEYUP,
				key
			))
			self.key_released(key)

	# Called once a key is released, for the user to override
	def key_released(self, key):
		return

	# Automates adding mouse pressed events for pygame style event handling
	def mousePressEvent(self, event):
		event.accept() # Accept the event by default, it is okay to call ignore later
		x = event.x()
		y = event.y()
		mouse_pos = (x, y)
		self.event.queue_event(mach.Event(
			mach.MOUSEBUTTONDOWN,
			pos = mouse_pos
		))
		self.mouse_pressed(event)

	# Called once a mouse button is pressed, for the user to override
	def mouse_pressed(self, event):
		return

	# Automates adding mouse movement events for pygame style event handling
	def mouseMoveEvent(self, event):
		event.accept() # Accept the event by default, it is okay to call ignore later
		x = event.x()
		y = event.y()
		mouse_pos = (x, y)
		self.event.queue_event(mach.Event(
			mach.MOUSEMOTION,
			pos = mouse_pos
		))
		self.mouse_moved(event)

	# Called once the mouse is moved, for the user to override
	def mouse_moved(self, event):
		return

	# Update our double buffer system
	def swap_buffers(self):
		self.context.swapBuffers(self)

	def bind(self):
		geom = self.getGeometry()
		width = geom.width
		height = geom.height

		# Bind any frame buffers
		glBindFramebuffer(GL_FRAMEBUFFER, 0)
		if sys.platform == 'win32':
			glViewport(8, 8, width, height)
		elif sys.platform == 'darwin':
			glViewport(0, 0, width, height)
		elif sys.platform == 'linux':
			glViewport(0, 0, width, height)

		# Bind any depth buffers
		glBindRenderbuffer(GL_RENDERBUFFER, 0)

	def getGeometry(self):
		geom = self.geometry()
		pgeom = self.parent().geometry()
		# if sys.platform == 'win32':
		# 	return Geometry(pgeom.x(), pgeom.y(), geom.width(), geom.height())
		# elif sys.platform == 'darwin':
		# 	return Geometry(pgeom.x(), pgeom.y(), geom.width(), geom.height())
		# elif sys.platform == 'linux':
		# 	return 'idk'
		return Geometry(pgeom.x(), pgeom.y(), geom.width(), geom.height())


class MainWindow(QMainWindow):
	def __init__(self, W, args):
		super().__init__()
		self.w = W(*args)
		widget = Qt.QWidget.createWindowContainer(self.w, None, Qt.Qt.Widget)
		self.setCentralWidget(widget)

	def closeEvent(self, event):
		self.w.closeEvent(event)

def initializa_app_with_window(W, width, height, args=()):
	app = Qt.QApplication([])

	window = MainWindow(W, args)
	window.show()

	# window = Qt.QWidget.createWindowContainer(W(*args), None, Qt.Qt.Widget)
	# window.show()
	window.resize(width, height)

	app.exec_()