import numpy
from OpenGL.GL import *

class Attribute:
	"""
	Organizes the data necessary to upload attribute data into a shader
	"""
	def __init__(self, data, location, size=3, dtype=numpy.float32, type=GL_FLOAT, normalized=GL_FALSE, stride=0):
		self.data = numpy.array(data, dtype=dtype)
		self.size = size
		self.location = location
		self.type = type
		self.normalized = normalized
		self.stride = stride
		self.bytes = self.data.nbytes

		self.count = self.data.size // self.size

	def setOffset(self, offset):
		self.offset = offset
