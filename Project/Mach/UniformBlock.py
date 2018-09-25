from ctypes import pointer
from OpenGL.GL import *
import numpy as np

uniformBound = -1
class UniformBlock:
	"""
	Organizes the usage of uniform blocks in glsl

	Arguments:
		shader - the shader object that the uniform block should be bound to
		name - the name of the uniform block
		index - the bind index of the uniform block
	"""
	def __init__(self, shader, name):
		self.name = name
		self.size = shader.GetUniformBlockSize(name)
		self.shader = shader
		self.index = self.shader.GetUniformIndex(name)

		loc = self.shader.GetBlockLocation(self.name)

		glUniformBlockBinding(self.shader.shader, loc, self.index)

		self.ubo = GLuint()
		glGenBuffers(1, pointer(self.ubo))

		self.bind()
		glBufferData(GL_UNIFORM_BUFFER, self.size, None, GL_STATIC_DRAW)
		glBindBufferRange(GL_UNIFORM_BUFFER, self.index, self.ubo, 0, self.size);

	def GetBlockUniformInfo(self, name):
		" Get a variable's offset and size"
		return self.shader.GetBlockUniformInfo(self.name, name)

	def GetStructSize(self, name):
		" Refers to shader for struct size"
		return self.shader.GetStructSize(name)

	def bind(self):
		" Bind this buffer"
		glBindBuffer(GL_UNIFORM_BUFFER, self.ubo)

	def autoBind(self):
		" Automatically bind this buffer if it is not already bound"
		if (uniformBound != self.ubo):
			self.bind()

	def storeMatrix4(self, name, data):
		"""
		Store a mat4

		Arguments:
			name - name of the variable within the uniform block (string)
			data - a numpy matrix
		"""
		self.autoBind()
		data = np.array(data.flatten(), dtype=np.float32)[0]

		offset, size = self.GetBlockUniformInfo(name)
		glBufferSubData(GL_UNIFORM_BUFFER, offset, size, data)

	def storeMatrix3(self, name, data):
		"""
		Store a mat3

		Arguments:
			name - name of the variable within the uniform block (string)
			data - a numpy matrix
		"""
		self.autoBind()
		arr = np.array([[m[0, 0], m[0, 1], m[0, 2], 0] for m in data], dtype=np.float32).flatten()

		offset, size = self.GetBlockUniformInfo(name)
		glBufferSubData(GL_UNIFORM_BUFFER, offset, size, arr)

	def storeMatrix3Array(self, name, data):
		"""
		Store a mat3 array

		Arguments:
			name - name of the variable within the uniform block (string)
			data - an iterable of numpy matrices
		"""
		self.autoBind()
		flattenedData = []
		for mat in data:
			arr = [[m[0, 0], m[0, 1], m[0, 2], 0] for m in mat]
			flattenedData.append(arr)

		flattenedData = np.array(flattenedData, dtype=np.float32).flatten()

		offset, size = self.GetBlockUniformInfo(name)
		glBufferSubData(GL_UNIFORM_BUFFER, offset, size, flattenedData)

	def storeMatrix4Array(self, name, data):
		"""
		Store a mat4 array

		Arguments:
			name - name of the variable within the uniform block (string)
			data - an iterable of numpy matrices
		"""
		self.autoBind()
		flattenedData = np.array([], dtype=np.float32)
		for d in data:
			flattenedData = np.append(flattenedData, d.flatten())
		flattenedData = np.array(flattenedData, dtype=np.float32)

		offset, size = self.GetBlockUniformInfo(name)
		glBufferSubData(GL_UNIFORM_BUFFER, offset, size, flattenedData)

	def storeFloat(self, name, *data):
		"""
		Store a float, vec2, vec3, or vec4

		Arguments:
			name - name of the variable within the uniform block (string)
			data - a set of float arguments
		"""
		self.autoBind()
		data = np.array(data, dtype=np.float32)

		offset, size = self.GetBlockUniformInfo(name)
		glBufferSubData(GL_UNIFORM_BUFFER, offset, size, data)

	def storeVec2Array(self, name, data):
		"""
		Store a vec2 array

		Arguments:
			name - name of the variable within the uniform block (string)
			data - an iterable of (iterables of size 2)
		"""
		flattenedData = []
		for vec in data:
			arr = [vec[0], vec[1], 0 , 0]
			flattenedData.append(arr)

		flattenedData = np.array(flattenedData, dtype=np.float32).flatten()

		offset, size = self.GetBlockUniformInfo(name)
		glBufferSubData(GL_UNIFORM_BUFFER, offset, size, flattenedData)

	def storeVec3Array(self, name, data):
		"""
		Store a vec3 array

		Arguments:
			name - name of the variable within the uniform block (string)
			data - an iterable of (iterables of size 3)
		"""
		flattenedData = []
		for vec in data:
			arr = [vec[0], vec[1], vec[2] , 0]
			flattenedData.append(arr)

		flattenedData = np.array(flattenedData, dtype=np.float32).flatten()

		offset, size = self.GetBlockUniformInfo(name)
		glBufferSubData(GL_UNIFORM_BUFFER, offset, size, flattenedData)

	def storeVec4Array(self, name, data):
		"""
		Store a vec4 array

		Arguments:
			name - name of the variable within the uniform block (string)
			data - an iterable of (iterables of size 4)
		"""
		flattenedData = []
		for vec in data:
			arr = [vec[0], vec[1], vec[2] , vec[3]]
			flattenedData.append(arr)

		flattenedData = np.array(flattenedData, dtype=np.float32).flatten()

		offset, size = self.GetBlockUniformInfo(name)
		glBufferSubData(GL_UNIFORM_BUFFER, offset, size, flattenedData)

	def storeFloatArray(self, name, data):
		"""
		Store an array of floats

		Arguments:
			name - name of the variable within the uniform block (string)
			data - an iterable of floats
		"""
		self.autoBind()
		data = [[n, 0, 0, 0] for n in data]
		data = np.array(data, dtype=np.float32).flatten()

		offset, size = self.GetBlockUniformInfo(name)

		glBufferSubData(GL_UNIFORM_BUFFER, offset, size, data)

	def storeInt(self, name, *data):
		"""
		Store an integer, ivec2, ivec3, ivec4

		Arguments:
			name - name of the variable within the uniform block (string)
			data - set of integer arguments
		"""
		self.autoBind()
		data = np.array(data, dtype=np.int32)

		offset, size = self.GetBlockUniformInfo(name)
		glBufferSubData(GL_UNIFORM_BUFFER, offset, size, data)

	def storeIntArray(self, name, data):
		"""
		Store an array of integers

		Arguments:
			name - name of the variable within the uniform block (string)
			data - an iterable of integers
		"""
		self.autoBind()
		data = [[n, 0, 0, 0] for n in data]
		data = np.array(data, dtype=np.int32).flatten()

		offset, size = self.GetBlockUniformInfo(name)
		glBufferSubData(GL_UNIFORM_BUFFER, offset, size, data)
