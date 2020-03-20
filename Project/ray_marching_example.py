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
		glDisable(GL_CULL_FACE)

		self.view = mach.ViewMatrix()
		self.view.pos = glm.vec3(0, 0, 50)
		self.view.target = glm.vec3(0)
		self.view.update()
		# self.view.set_rotation(0, np.pi / 2)
		self.perspective = mach.PerspectiveCamera(self.size[0], self.size[1])

		self.scale = 0

		self.ray_marching_shader = mach.Shader(
			mach.resource_path('ray_marching/vert.glsl'),
			mach.resource_path('ray_marching/frag.glsl')
		)
		self.ray_marching_shader.store_matrix4('view_matrix', glm.inverse(self.view.mat))
		self.ray_marching_shader.store_matrix4('perspective_matrix', glm.inverse(self.perspective.mat))
		self.ray_marching_shader.store_float('scale', self.scale)
		self.ray_marching_shader.store_float('ball_position', glm.vec3(0, 0, 48))

		vertices = np.array([
			[1, 1, -1],
			[-1, 1, -1],
			[-1, -1, -1],
			[1, -1, -1]
		], dtype=np.float32)

		indices = np.array([
			0, 1, 2,
			0, 2, 3
		], dtype=np.int32)

		attributes = [
			mach.Attribute(vertices, 0)
		]

		self.quad = self.ray_marching_shader.create_new_mach_object()
		self.quad.store_attribute_array(attributes)
		self.quad.store_element_index_array(indices)
		self.quad.bind()

		self.set_FPS(60)

	def draw(self, delta_time):
		self.clear()

		self.bind()
		self.ray_marching_shader.bind()
		self.quad.draw()
		self.swap_buffers()

		print(self.get_FPS())

		move = glm.vec3(0)
		if self.keys_pressed[mach.Key_Left] or self.keys_pressed[mach.Key_A]:
			move += glm.vec3(-1, 0, 0)
		if self.keys_pressed[mach.Key_Right] or self.keys_pressed[mach.Key_D]:
			move += glm.vec3(1, 0, 0)
		if self.keys_pressed[mach.Key_Up] or self.keys_pressed[mach.Key_W]:
			move += glm.vec3(0, 0, -1)
		if self.keys_pressed[mach.Key_Down] or self.keys_pressed[mach.Key_S]:
			move += glm.vec3(0, 0, 1)
		if move != glm.vec3(0):
			self.view.move_rel(glm.normalize(move) * 0.1)
			self.view.update()
			self.ray_marching_shader.store_matrix4('view_matrix', glm.inverse(self.view.mat))

		if self.keys_pressed[mach.Key_Space]:
			self.scale += 0.003
			self.ray_marching_shader.store_float('scale', self.scale)

		for event in self.event.get():
			if event.type == mach.QUIT:
				# self.texture.save('test.png')
				self.close()
			# elif event.type == mach.VIDEOEXPOSE:
				# self.camera.resize(self.size[0], self.size[1])
				# self.camera.update_projection_matrix('projection_matrix', [self.ray_marching_shader])
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
			self.ray_marching_shader.store_matrix4('view_matrix', glm.inverse(self.view.mat))

	def on_expose(self, event):
		self.perspective.resize(self.size[0], self.size[1])
		self.ray_marching_shader.store_matrix4('perspective_matrix', glm.inverse(self.perspective.mat))

if __name__ == "__main__":
	# create the QT App and window
	aspect_ratio = 1

	height = 600
	width = int(aspect_ratio * height)
	mach.run_app_with_window(Game, width, height)
