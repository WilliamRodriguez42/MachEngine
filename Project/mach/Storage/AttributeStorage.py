from OpenGL.GL import *
from ctypes import c_void_p
import numpy as np

class AttributeStorage:
	def __init__(self):
		self.attributes = []
		self.VBO = glGenBuffers(1)
		self.IBO = None
		self.IBOSize = 0
		self.count = 0

	def bind_attributes(self):
		" Binds all of the user defined attributes for drawing"
		glBindBuffer(GL_ARRAY_BUFFER, self.VBO)

		# Check if indexing is enabled
		if self.IBO is not None:
			glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.IBO)

		for attr in self.attributes:
			glVertexAttribPointer(
						attr.location,
						attr.size,
						attr.type,
						attr.normalized,
						attr.stride,
						c_void_p(attr.offset))

			glEnableVertexAttribArray(attr.location)

	def store_attribute_array(self, attributes):
		"""
		Converts attributes to bytes and stores them, only happens once

		Arguments:
			attributes - A list of Attribute objects
		"""
		self.attributes = attributes

		# Combine all of the attribute data into one data array
		data = bytearray()
		offset = 0
		for attr in attributes:
			attr.set_offset(offset)
			offset += attr.data.nbytes
			data.extend(attr.data.tobytes())

		# Store the count for the vertices if we are not using indexing
		if (self.IBO is None):
			self.count = attributes[0].count

		glBindBuffer(GL_ARRAY_BUFFER, self.VBO)

		glBufferData(
					GL_ARRAY_BUFFER,
					offset,
					bytes(data),
					GL_STATIC_DRAW
					)

	def store_element_index_array(self, indices):
		"""
		Stores and enables an array of indices for element drawing

		Arguments:
			indices - 1D numpy array of integers
		"""

		self.IBO = glGenBuffers(1)
		self.IBOSize = indices.nbytes
		self.count = len(indices)

		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.IBO)
		glBufferData(
			GL_ELEMENT_ARRAY_BUFFER,
			indices.nbytes,
			indices.tobytes(),
			GL_STATIC_DRAW
		)
