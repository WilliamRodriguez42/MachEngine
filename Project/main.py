# from Mach.Shader import *
# from Mach.Mach import *
import mach
from OpenGL.GL import *
import glm
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

class Game(mach.Window):
	mouse_captured = False

	def start(self):
		self.box_shader = mach.Shader(
			mach.resource_path('boxvert.glsl'),
			mach.resource_path('boxfrag.glsl')
		)

		self.perspective = mach.PerspectiveCamera(self.size[0], self.size[1])
		self.view = mach.ViewMatrix()

		self.box_shader.store_matrix4('projection_matrix', self.perspective.mat)
		self.box_shader.store_matrix4('view_matrix', self.view.mat)

		# self.box_shader.store_sampler2D_from_numpy('test', np.random.rand(100, 20, 3).astype(np.float32), format=GL_RGB)
		box_vertices = np.array([
			[0, 1, 0],
			[0, 0, 0],
			[1, 1, 0],
			# [1, 1, 0],
			[1, 0, 0],
			# [0, 0, 0],
		], dtype=np.float32)

		tex_coords = np.array([
			[0, 1],
			[0, 0],
			[1, 1],
			[1, 0],
		], dtype=np.float32)

		indices = np.array([
			0, 1, 2,
			1, 3, 2
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
		self.box_shader.store_sampler2D_from_path('test', mach.resource_path('guy.png'))

	def draw(self, delta_time):
		self.clear()

		# self.texture.bind()
		self.box_shader.bind()
		self.box.bind()
		self.box.draw()
		self.swap_buffers()

		move = glm.vec3(0)
		if self.keys_pressed[mach.Key_Left] or self.keys_pressed[mach.Key_A]:
			move += glm.vec3(-1, 0, 0)
		if self.keys_pressed[mach.Key_Right] or self.keys_pressed[mach.Key_D]:
			move += glm.vec3(1, 0, 0)
		if self.keys_pressed[mach.Key_Up] or self.keys_pressed[mach.Key_W]:
			move += glm.vec3(0, 0, 1)
		if self.keys_pressed[mach.Key_Down] or self.keys_pressed[mach.Key_S]:
			move += glm.vec3(0, 0, -1)
		if move != glm.vec3(0):
			self.view.move_rel_no_y(glm.normalize(move) * 0.1)
			self.view.update()
			self.box_shader.store_matrix4('view_matrix', self.view.mat)

		for event in self.event.get():
			if event.type == mach.QUIT:
				# self.texture.save('test.png')
				self.close()
			# elif event.type == mach.VIDEOEXPOSE:
				# self.camera.resize(self.size[0], self.size[1])
				# self.camera.update_projection_matrix('projection_matrix', [self.box_shader])
			elif event.type == mach.KEYDOWN:
				if event.key == mach.Key_Escape:
					self.mouse_captured = False
					self.setCursor(Qt.Qt.ArrowCursor)
			elif event.type == mach.MOUSEBUTTONDOWN:
				if not self.mouse_captured:
					self.setCursor(Qt.Qt.BlankCursor)
					center = self.size // 2
					self.set_mouse_pos(center)
					self.mouse_captured = True

	def on_mouse_move(self, event):
		if self.mouse_captured:
			center = self.size // 2
			mouse_delta = self.mouse_pos - center
			self.set_mouse_pos(center)

			yaw, pitch = mouse_delta * 0.001
			self.view.rotate(pitch, yaw)
			self.view.update()
			self.box_shader.store_matrix4('view_matrix', self.view.mat)

	def on_expose(self, event):
		self.perspective.resize(self.size[0], self.size[1])
		self.box_shader.store_matrix4('projection_matrix', self.perspective.mat)


if __name__ == "__main__":
	# create the QT App and window
	aspect_ratio = 16/9
	height = 600
	width = int(aspect_ratio * height)
	mach.run_app_with_window(Game, width, height)
