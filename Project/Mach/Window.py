# PyQT5 imports
from PyQt5 import Qt, QtGui
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QOpenGLContext, QSurfaceFormat, QWindow
from PyQt5.QtCore import QTimer, QElapsedTimer

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
import numpy as np

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
		self.make_current()

		# OpenGL settings
		glEnable(GL_DEPTH_TEST)
		glDepthMask(GL_TRUE)
		glDepthFunc(GL_LEQUAL)

		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

		# A list of keys that are currently being pressed
		self.keys_held_down = []

		# A list of mouse buttons that are currently being pressed
		self.mouse_buttons_held_down = np.zeros(17, dtype=np.bool)

		# Start handling events in a way similar to pygame
		self.event = mach.EventManager()

		# Don't actually start rendering until the expose event is called
		self.exposed = threading.Event() 

		# Default for sixty frames per second
		self.FPS = 60

		# Timer responsible for controlling the update loop
		self.update_timer = QTimer()

		# Timer for determining elapsed time between frames
		self.timer = QElapsedTimer()
		self.timer.start()
		self.frame_times = [0] * 10 # Store the last 10 frame time deltas
		# print([d for d in dir(self) if d.endswith('Event')]) # Print all possible event handlers

		# Default mouse position
		self.cursor = QtGui.QCursor()
		self.mouse_pos = np.zeros(2, dtype=np.int) # Cannot initialize mouse position until object is attached to parent

		# Keep track of where the close event comes from
		self.close_user_requested = False

	def start(self):
		return

	def draw(self):
		return

	def set_FPS(self, FPS):
		self.exposed.wait()
		self.FPS = FPS
		self.update_timer.start(1 / self.FPS * 1000)

	def get_mouse_pos(self):
		return np.array((self.cursor.pos().x(), self.cursor.pos().y()), dtype=np.int) - self.pos

	def set_mouse_pos(self, pos):
		self.cursor.setPos(*(self.pos + pos))

	def get_window_size(self):
		geom = self.get_geometry()
		return np.array((geom.width, geom.height), dtype=np.int)

	def get_window_pos(self):
		geom = self.get_geometry()
		return np.array((geom.x, geom.y), dtype=np.int)

	# Make the opengl context held in this window current
	def make_current(self):
		self.context.makeCurrent(self)

	def clear(self):
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

	# Update the screen
	def update(self):
		# self.make_current()
		# print(self.isClosing())
		self.draw()

		# Store information to calculate FPS
		current_time = self.timer.elapsed()
		self.frame_times.append(current_time / 1000)
		del self.frame_times[0]

	# Gets the average of the recorded FPS for the last ten frames
	def get_FPS(self):
		return 10 / (self.frame_times[-1] - self.frame_times[0] + 1e-8)

	# Automatically handle window moved events for pygame style events
	def moveEvent(self, event):
		event.accept() # Accept the event by default, it is okay to call ignore later
		if self.parent() is None:
			return

		self.pos = self.get_window_pos()
		self.event.queue_event(mach.Event(
			mach.VIDEOMOVED,
			event,
			pos = self.pos
		))
		self.on_window_move(event)

	# Called when the window is moved, for ther user to override
	def on_window_move(self, event):
		pass

	# Handle video expose / resize events
	def exposeEvent(self, event):
		event.accept()
		if self.parent() is None or (self.exposed.is_set() and not self.update_timer.isActive()):
			return

		self.size = self.get_window_size()
		self.bind()

		if self.isExposed() and self.isVisible():
			if not self.exposed.is_set():
				self.exposed.set()
				self.start()

				# Start the update thread
				self.update_timer.timeout.connect(self.update)
				self.update_timer.start(1 / self.FPS * 1000)

		self.event.queue_event(mach.Event(
			mach.VIDEOEXPOSE,
			event,
			size = self.size
		))

		if self.update_timer.isActive():
			self.on_window_expose(event)
			self.update_timer.start()

	# Called once the mouse is resized, for the user to override
	def on_window_expose(self, event):
		return

	def resizeEvent(self, event):
		event.accept()
		if self.parent() is None or not self.exposed.is_set():
			return

		self.size = self.get_window_size()
		self.event.queue_event(mach.Event(
			mach.VIDEORESIZE,
			event,
			size = self.size
		))
		if self.update_timer.isActive():
			self.on_window_resize(event)

	def on_window_resize(self, event):
		return

	# Automate window close events for pygame style event handling
	def closeEvent(self, event):
		if self.close_user_requested:
			event.accept()
			return

		event.ignore() # Ignore the event by default, it is okay to call accept later
		self.event.queue_event(mach.Event(
			mach.QUIT,
			event
		))
		self.on_close(event)
		if event.isAccepted():
			self.update_timer.stop()

	# Called once the user attempts to close the application, for the user to override
	def on_close(self, event):
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
					event,
					key = key
				))
				self.on_key_press(key)

	# Called once every time a key is pressed, for the user to override
	def on_key_press(self, key):
		return

	# Automates key released events for pygame style event handling
	def keyReleaseEvent(self, event):
		event.accept() # Accept the event by default, it is okay to call ignore later
		if not event.isAutoRepeat():
			key = event.key()
			self.keys_held_down.remove(key)
			self.event.queue_event(mach.Event(
				mach.KEYUP,
				event,
				key = key
			))
			self.on_key_release(key)

	# Called once a key is released, for the user to override
	def on_key_release(self, key):
		return

	# Automates adding mouse pressed events for pygame style event handling
	def mousePressEvent(self, event):
		event.accept() # Accept the event by default, it is okay to call ignore later
		self.mouse_buttons_held_down[event.button()] = True
		self.event.queue_event(mach.Event(
			mach.MOUSEBUTTONDOWN,
			event,
			pos = self.mouse_pos,
			button = event.button()
		))
		self.on_mouse_press(event)

	# Called once a mouse button is pressed, for the user to override
	def on_mouse_press(self, event):
		return

	# Automates adding mouse movement events for pygame style event handling
	def mouseMoveEvent(self, event):
		event.accept() # Accept the event by default, it is okay to call ignore later
		self.mouse_pos = self.get_mouse_pos()
		self.event.queue_event(mach.Event(
			mach.MOUSEMOTION,
			event,
			pos = self.mouse_pos
		))
		self.on_mouse_move(event)

	# Called once the mouse is moved, for the user to override
	def on_mouse_move(self, event):
		return

	def mouseReleaseEvent(self, event):
		event.accept()
		self.mouse_buttons_held_down[event.button()] = False
		self.event.queue_event(mach.Event(
			mach.MOUSEBUTTONUP,
			event,
			pos = self.mouse_pos,
			button = event.button()
		))
		self.on_mouse_release(event)

	def on_mouse_release(self, event):
		return

	def mouseDoubleClickEvent(self, event):
		event.accept()
		self.event.queue_event(mach.Event(
			mach.MOUSEBUTTONDOUBLECLICKED,
			event,
			pos = self.mouse_pos,
			button = event.button()
		))
		self.on_mouse_double_click(event)

	def on_mouse_double_click(self, event):
		return

	def wheelEvent(self, event):
		event.accept()
		self.event.queue_event(mach.Event(
			mach.MOUSEWHEEL,
			event,
			pos = self.mouse_pos,
			angle_delta = event.angleDelta(),
			pixel_delta = event.pixelDelta()
		))
		self.on_mouse_wheel(event)

	def on_mouse_wheel(self, event):
		return

	def focusInEvent(self, event):
		event.accept()
		self.event.queue_event(mach.Event(
			mach.FOCUSIN,
			event
		))
		self.on_focus_in(event)
	
	def on_focus_in(self, event):
		return

	def focusOutEvent(self, event):
		event.accept()
		self.event.queue_event(mach.Event(
			mach.FOCUSOUT,
			event
		))
		self.on_focus_out(event)

	def on_focus_out(self, event):
		return

	def hideEvent(self, event):
		event.accept()
		self.event.queue_event(mach.Event(
			mach.HIDE,
			event
		))
		self.on_hide(event)

	def on_hide(self, event):
		return

	def showEvent(self, event):
		event.accept()
		self.event.queue_event(mach.Event(
			mach.SHOW,
			event
		))
		self.on_show(event)

	def on_show(self, event):
		return

	def tabletEvent(self, event):
		event.accept()
		self.event.queue_event(mach.Event(
			mach.TABLET,
			event
		))
		self.on_tablet(event)

	def on_tablet(self, event):
		return

	def touchEvent(self, event):
		event.accept()
		self.event.queue_event(mach.Event(
			mach.TOUCH,
			event
		))
		self.on_touch(event)

	def on_touch(self, event):
		return

	# Update our double buffer system
	def swap_buffers(self):
		self.context.swapBuffers(self)

	def bind(self):
		width = self.size[0]
		height = self.size[1]

		# Bind any frame buffers
		glBindFramebuffer(GL_FRAMEBUFFER, 0)
		if sys.platform == 'win32':
			glViewport(8, 8, width, height) # Windows is stupid and shifts the viewport by 8 pixels in both axes
		elif sys.platform == 'darwin':
			glViewport(0, 0, width, height)
		elif sys.platform == 'linux':
			glViewport(0, 0, width, height)

	def get_geometry(self):
		geom = self.geometry()
		pgeom = self.parent().geometry()
		# if sys.platform == 'win32':
		# 	return Geometry(pgeom.x(), pgeom.y(), geom.width(), geom.height())
		# elif sys.platform == 'darwin':
		# 	return Geometry(pgeom.x(), pgeom.y(), geom.width(), geom.height())
		# elif sys.platform == 'linux':
		# 	return 'idk'
		return Geometry(pgeom.x(), pgeom.y(), geom.width(), geom.height())

	def close(self):
		# Call parent().close(), which will call our closeEvent. Since this function was requested by the user, bypass on_close and accept the event
		self.close_user_requested = True
		self.update_timer.stop()
		self.parent().close()
		super().close() # Not sure if this is needed but it doesn't hurt

class MainWindow(QMainWindow):
	def __init__(self, W, args):
		super().__init__()
		self.w = W(*args)
		widget = Qt.QWidget.createWindowContainer(self.w, None, Qt.Qt.Widget)
		self.setCentralWidget(widget)

	def closeEvent(self, event):
		self.w.closeEvent(event)

	def moveEvent(self, event):
		self.w.moveEvent(event)

def run_app_with_window(W, width, height, args=()):
	app = Qt.QApplication([])

	window = MainWindow(W, args)
	window.show()

	# window = Qt.QWidget.createWindowContainer(W(*args), None, Qt.Qt.Widget)
	# window.show()
	window.resize(width, height)

	app.exec_()