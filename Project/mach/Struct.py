import numpy as np
from OpenGL.GL import *

class Struct:
	"""
	Organizes the usage of struct objects

	arguments:
		uniform - the UniformBlock object (found in Mach.UniformBlock) that this struct will be bound to
		name - the name of the struct in the glsl (string)
		variableName - the name of the variable referenced in glsl (string)
		index - if the struct is an item in an array of structs, use the index to specify the position in the array (integer)
	"""
	def __init__(self, uniform, name, variableName, index=-1):
		self.name = name
		self.variableName = variableName
		self.uniform = uniform
		self.shader = uniform.shader
		self.index = index

		self.uoffset, self.usize = self.uniform.GetBlockUniformInfo(variableName)
		self.structSize = self.shader.GetStructSize(self.name)

	def GetUniformInfo(self, name):
		" Gets the offset and size of the struct object"
		if (self.index < 0):
			offset, size = self.shader.GetStructUniformInfo(self.name, name)
			return (self.uoffset + offset, size)
		else:
			offset, size = self.shader.GetStructUniformInfo(self.name, name)
			return (self.uoffset + offset + (self.structSize * self.index), size)

	def autoBind(self):
		" Automatically bind the parent uniform if it is not already bound"
		self.uniform.autoBind()

	def storeMatrix4(self, name, data):
		"""
		Store a mat4

		Arguments:
			name - name of the variable within the uniform block (string)
			data - a numpy matrix
		"""
		self.autoBind()
		data = np.array(data.flatten(), dtype=np.float32)[0]

		offset, size = self.GetUniformInfo(name)
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

		offset, size = self.GetUniformInfo(name)
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

		offset, size = self.GetUniformInfo(name)
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

		offset, size = self.GetUniformInfo(name)
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

		offset, size = self.GetUniformInfo(name)
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

		offset, size = self.GetUniformInfo(name)
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

		offset, size = self.GetUniformInfo(name)
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

		offset, size = self.GetUniformInfo(name)
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

		offset, size = self.GetUniformInfo(name)

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

		offset, size = self.GetUniformInfo(name)
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

		offset, size = self.GetUniformInfo(name)
		glBufferSubData(GL_UNIFORM_BUFFER, offset, size, data)
