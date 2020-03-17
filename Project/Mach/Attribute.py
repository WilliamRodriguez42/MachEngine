import numpy
from OpenGL.GL import *

class Attribute:
	"""
	Organizes the data necessary to upload attribute data into a shader
	"""
	def __init__(self, data, location, type=GL_FLOAT, normalized=GL_FALSE, stride=0):
		self.data = data.reshape(-1)
		self.size = data.shape[1]
		self.location = location
		self.type = type
		self.normalized = normalized
		self.stride = stride
		self.bytes = self.data.nbytes

		self.count = self.data.size // self.size

	def set_offset(self, offset):
		self.offset = offset
