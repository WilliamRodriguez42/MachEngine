# from Mach.Shader import *
# from Mach.Mach import *
import mach
from OpenGL.GL import *
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

aspect_ratio = 16/9

class Game(mach.Window):
	captureMouse = True
	mouse_captured = False

	def start(self):
		self.camera = mach.OrthoScreenCamera(width, height, aspect_ratio, 0.1, 100, 1)
		self.box_shader = mach.Shader(
			mach.resource_path('boxvert.glsl'),
			mach.resource_path('boxfrag.glsl')
		)
		# self.box_shader.store_sampler2D_from_numpy('test', np.random.rand(100, 20, 3).astype(np.float32), format=GL_RGB)
		self.box_shader.store_sampler2D_from_path('test', mach.resource_path('guy.png'))
		box_vertices = np.array([
			[1, 1, 0],
			[0, 0, 0],
			[0, 1, 0],
			# [1, 1, 0],
			[1, 0, 0],
			# [0, 0, 0],
		], dtype=np.float32)

		tex_coords = np.array([
			[1, 1],
			[0, 0],
			[0, 1],
			[1, 0],
		], dtype=np.float32)

		indices = np.array([
			0, 1, 2,
			0, 3, 1
		], dtype=np.int32)

		attributes = [
			mach.Attribute(box_vertices, 0),
			mach.Attribute(tex_coords, 1)
		]

		self.box = self.box_shader.create_new_mach_object()
		self.box.store_attribute_array(attributes)
		self.box.store_element_index_array(indices)
		self.box.store_float('color', (1, 0, 0, 1))
		self.box.store_float('box', (-aspect_ratio, -1, aspect_ratio, 1))
		self.box.bind()

		self.camera.resize(self.size[0], self.size[1])
		self.camera.update_projection_matrix('projection_matrix', [self.box_shader])

		self.texture = mach.DepthTexture(1066, 600)
		self.bind()

	def draw(self):
		self.clear()

		# self.texture.bind()
		self.box_shader.bind()
		self.box.bind()
		self.box.draw()
		self.swap_buffers()

		for event in self.event.get():
			if event.type == mach.QUIT:
				self.texture.save('test.png')
				self.close()
			elif event.type == mach.MOUSEMOTION:
				if self.mouse_captured:
					center = self.size // 2
					mouse_delta = self.mouse_pos - center
					self.set_mouse_pos(center)
			elif event.type == mach.VIDEOEXPOSE:
				self.camera.resize(self.size[0], self.size[1])
				self.camera.update_projection_matrix('projection_matrix', [self.box_shader])
			elif event.type == mach.KEYDOWN:
				if event.key == mach.Key_Escape:
					self.mouse_captured = False
					self.setCursor(Qt.Qt.ArrowCursor)
			elif event.type == mach.MOUSEBUTTONDOWN:
				if self.captureMouse and not self.mouse_captured:
					self.setCursor(Qt.Qt.BlankCursor)
					center = self.size // 2 + self.pos
					self.set_mouse_pos(center)
					self.mouse_captured = True

if __name__ == "__main__":
	# create the QT App and window
	width = 1066
	height = 600
	mach.run_app_with_window(Game, width, height)
