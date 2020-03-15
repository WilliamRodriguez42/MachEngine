# from Mach.Shader import *
# from Mach.Mach import *
import mach
# from Mach.Rendered import Texture, DepthTexture
# from Mach.Camera import Camera
# from Mach.UniformBlock import UniformBlock
# from Mach.Struct import Struct
# from Mach.Matrix import *
# from Mach.Camera import *
# import Mach.TextureAtlas as ta

# import Mega.PlayerManager as pm
# import Mega.HitAndHurt as hnh
# import Mega.RenderObject as ren
# import Mega.MegaObject as mo
# from Mega.Scene import Scene

from PyQt5 import Qt, QtGui, QtCore
import numpy as np

import sys

aspect_ratio = 16/9

class Game(mach.Window):
	captureMouse = True
	mouseCaptured = False

	def start(self):
		self.camera = mach.OrthoScreenCamera(width, height, aspect_ratio, 0.1, 100, 1)
		self.box_shader = mach.Shader(
			mach.resource_path('boxvert.glsl'),
			mach.resource_path('boxfrag.glsl')
		)

		box_vertices = [
			1, 1, 0,
			0, 0, 0,
			0, 1, 0,
			1, 1, 0,
			1, 0, 0,
			0, 0, 0,
		]

		attributes = [
			mach.Attribute(box_vertices, 0, size=3, dtype=np.float32)
		]

		self.box = self.box_shader.createNewMachObject()
		self.box.storeAttributeArray(attributes)
		self.box.storeFloat('color', 1, 0, 0, 1)
		self.box.bind()

	def draw(self):
		self.clear()
		self.box_shader.bind()
		self.box.storeFloat('box', -aspect_ratio, -1, aspect_ratio, 1)
		self.box.bind()
		self.box.draw()
		self.swap_buffers()

		# print(self.event.get())
		self.event.get()

	def window_resized(self, width, height):
		self.bind()
		self.camera.resize(width, height)
		self.camera.updateObjects('projectionMatrix', [self.box_shader])
		self.draw()

	# Key handling
	def key_pressed(self, key):
		if key == QtCore.Qt.Key_Escape:
			self.mouseCaptured = False
			self.setCursor(Qt.Qt.ArrowCursor)

	# Mouse events
	def mouse_pressed(self, event):
		x = event.x()
		y = event.y()

		# Capture the mouse
		if self.captureMouse and not self.mouseCaptured:
			self.setCursor(Qt.Qt.BlankCursor)

			cursor = QtGui.QCursor()

			geom = self.getGeometry()
			originX = geom.width / 2
			originY = geom.height / 2
			cursor.setPos(int(geom.x + originX), int(geom.y + originY))

			self.mouseCaptured = True

	def mouse_moved(self, event):
		x = event.x()
		y = event.y()

		if self.mouseCaptured:
			geom = self.getGeometry()

			originX = geom.width / 2
			originY = geom.height / 2

			deltaX = x - originX
			deltaY = y - originY

			cursor = QtGui.QCursor()
			cursor.setPos(int(geom.x + originX), int(geom.y + originY))

if __name__ == "__main__":
	# create the QT App and window
	width = 1066
	height = 600
	mach.initializa_app_with_window(Game, width, height, args=())
	print("Exiting")
