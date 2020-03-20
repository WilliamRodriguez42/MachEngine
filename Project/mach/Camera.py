# from Mach.Matrix import *
import mach
import numpy as np
import glm
import math

# Define the up vector in world coordinates
UP = glm.vec3(0, 1, 0)

class OrthographicCamera:
	def __init__(self, width, height, aspect_ratio, near_clip, far_clip, zoom = 1):
		"""
		Creates an orthographic matrix used for rendering to the screen
		Takes in the width and height of the screen in pixels
		as well as the desired aspect_ratio ratio in width / heigth
		the near_clip and far_clip express the desired clipping ranges of the matrix
		and the zoom allows the user to multiply the upper and lower ranges of the x and y axis by a scalar

		the +y is limited to zoom
		the -y is limited to -zoom
		the +x is limited to zoom * aspect_ratio
		the -x is limited to -zoom * aspect_ratio
		"""
		self.near_clip = near_clip
		self.far_clip = far_clip
		self.zoom = zoom
		self.aspect_ratio = aspect_ratio
		self.width = width
		self.height = height
		self.resize(width, height)

	def update_projection_matrix(self, matrix_name, objects):
		"""
		Takes in a list of MachObjects or Shaders and will fill out a uniform with the name matrix_name with our OrthographicMatrix
		"""
		for o in objects:
			o.store_matrix4(matrix_name, self.mat)

	def resize(self, width = 0, height = 0, zoom = 0):
		"""
		Resizes our matrix to fit a new screen width and height, or will zoom the screen
		"""
		if width > 0: self.width = width
		if height > 0: self.height = height
		if zoom > 0: self.zoom = zoom

		if width > self.aspect_ratio * height:
			aspect_ratio = 1 / (height * self.zoom)
		else:
			aspect_ratio = self.aspect_ratio / (width * self.zoom)
		self.mat = mach.OrthographicMatrix(-width * aspect_ratio, width * aspect_ratio, -height * aspect_ratio, height * aspect_ratio, self.near_clip, self.far_clip)

class PerspectiveCamera:
	def __init__(self, width, height, FOV=60, z_near=0.1, z_far=100):
		self.FOV = math.radians(FOV)
		self.z_near = z_near
		self.z_far = z_far
		self.aspect_ratio = width / height
		self.update()

	def resize(self, width, height):
		self.aspect_ratio = width / height
		self.update()

	def update(self):
		self.mat = glm.perspective(self.FOV, self.aspect_ratio, self.z_near, self.z_far)

class ViewMatrix:
	def __init__(self):
		self.pos = glm.vec3(0, 0, 3)
		self.target = glm.vec3(0, 0, 0)
		self.mat = glm.lookAt(self.pos, self.target, UP)
		self.polar = glm.polar(self.target - self.pos)

		self.pitch_max = math.radians(89)
		self.pitch_min = math.radians(-89)

	def move_rel(self, delta, locked=False):
		"""
		Translate by delta relative to the current position
			delta - glm.vec3 change in position
			locked - (boolean) should the camera stay fixed on the target
		"""
		delta = glm.vec3(glm.vec4(*delta, 1) * self.mat)
		self.pos += delta
		if not locked: self.target += delta

	def move_rel_no_y(self, delta, locked=False):
		"""
		Translate by delta relative to the current position, removing any component in the y direction
			delta - glm.vec3 change in position
			locked - (boolean) should the camera stay fixed on the target
		"""
		forward = self.target - self.pos
		forward.y = 0
		forward = glm.normalize(forward)
		right = glm.cross(forward, UP)

		local_delta = glm.vec3(0)
		local_delta.x = glm.dot(right, delta)
		local_delta.z = glm.dot(forward, delta)
		self.pos += local_delta
		if not locked: self.target += local_delta

	def move(self, delta, locked=False):
		self.pos += delta
		if not locked: self.target += delta

	def set_position(self, pos, locked=False):
		if locked:
			self.pos = pos
		else:
			delta = self.target - self.pos
			self.pos = pos
			self.target = delta + pos

	def rotate(self, pitch, yaw):
		self.polar[0] = max(min(self.polar[0] - pitch, self.pitch_max), self.pitch_min)
		self.polar[1] -= yaw
		self.target = glm.euclidean(self.polar.xy) + self.pos

	def set_rotation(self, pitch, yaw):
		self.polar[0] = max(min(-pitch, self.pitch_max), self.pitch_min)
		self.polar[1] = -yaw
		self.target = glm.euclidean(self.polar.xy) + self.pos

	def update(self):
		self.mat = glm.lookAt(self.pos, self.target, UP)
