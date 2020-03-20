from OpenGL.GL import *
import numpy as np
from ctypes import c_float
from collections.abc import Iterable

float_functions = {
	1: glUniform1f,
	2: glUniform2f,
	3: glUniform3f,
	4: glUniform4f
}

int_functions = {
	1: glUniform1i,
	2: glUniform2i,
	3: glUniform3i,
	4: glUniform4i
}

class UniformStorage:
	def __init__(self):
		self.uniforms = {}

	def bind_uniforms(self):
		" Binds all of the object specific uniforms"
		for name in self.uniforms:
			args, func = self.uniforms[name]
			func(*args)

	def store_float(self, name, vals):
		"""
		Store a float or a vector of floats

		Arguments:
			name - the name of the uniform variable (string)
			vals - a set of float arguments
		"""
		if not isinstance(vals, Iterable):
			loc = self.get_uniform_location(name)
			self.uniforms[name] = ((loc, vals), float_functions[1])
			return

		if len(vals) > 4:
			print("Cannot store more than four values for " + name)
			return
		loc = self.get_uniform_location(name)
		self.uniforms[name] = ((loc, *vals), float_functions[len(vals)])

	def store_int(self, name, vals):
		"""
		Store a int or vector of ints

		Arguments:
			name - the name of the uniform variable (string)
			vals - a set of integer arguments
		"""
		if len(vals) > 4:
			print("Cannot store more than four values for " + name)
			return
		loc = self.get_uniform_location(name)
		self.uniforms[name] = ((loc, *vals), int_functions[len(vals)])

	def store_matrix3(self, name, mat):
		"""
		Store a mat3

		Arguments:
			name - the name of the uniform variable (string)
			mat - a numpy matrix
		"""
		value = np.array(mat).flatten()

		loc = self.get_uniform_location(name)
		self.uniforms[name] = ((loc, (c_float * 9)(*value)), glUniformMatrix3fv)

	def store_matrix4(self, name, mat):
		"""
		Store a mat4

		Arguments:
			name - the name of the uniform variable (string)
			mat - a numpy matrix
		"""
		value = np.array(mat).flatten()

		loc = self.get_uniform_location(name)
		self.uniforms[name] = ((loc, 1, False, (c_float * 16)(*value)), glUniformMatrix4fv)
