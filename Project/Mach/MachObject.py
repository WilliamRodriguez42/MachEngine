from OpenGL.GL import *
from ctypes import c_void_p, c_float
from PIL import Image
import numpy

floatFunctions = {
	1: glUniform1f,
	2: glUniform2f,
	3: glUniform3f,
	4: glUniform4f
}

intFunctions = {
	1: glUniform1i,
	2: glUniform2i,
	3: glUniform3i,
	4: glUniform4i
}

class MachObject:
	"""
	Organizes the usage of individual uniforms and AttributeObjects,
	In other words it's a vertex list and all of the data that needs to go with it

	Arguments:
		shader - the shader object this object is bound to
		drawType - How the vertices are going to be drawn
	"""
	def __init__(self, shader, drawType=GL_TRIANGLES):
		self.drawType = drawType
		self.count = 0
		self.shader = shader
		self.VBO = glGenBuffers(1)
		self.IBO = None
		self.IBOSize = 0
		self.attributes = []
		self.images = {}
		self.uniforms = {}
		self.blocks = {}

	def bind(self, skipAttributes=False, skipImages=False, skipUniforms=False, skipBlocks=False):
		" Bind our vertex buffer and attributes for drawing"
		glBindBuffer(GL_ARRAY_BUFFER, self.VBO)

		# Check if indexing is enabled
		if (self.IBO is not None):
			glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.IBO)

		if not skipAttributes: 	self.bindAttributes()
		if not skipImages: 		self.bindImages()
		if not skipUniforms: 	self.bindUniforms()
		if not skipBlocks:		self.bindUniformBlocks()

	def draw(self):
		" Draw our object"
		if (self.IBO is None):
			glDrawArrays(self.drawType, 0, self.count)
		else:
			glDrawElements(self.drawType, self.count, GL_UNSIGNED_INT, None)

	def bindAttributes(self):
		" Binds all of the user defined attributes for drawing (Usually not called by user)"
		for attr in self.attributes:
			glVertexAttribPointer(
						attr.location,
						attr.size,
						attr.type,
						attr.normalized,
						attr.stride,
						c_void_p(attr.offset))

			glEnableVertexAttribArray(attr.location)

	def storeUniformBlock(self, uniformBlock):
		"""
		Stores a uniformBlock to be bound

		Arguments:
			uniformBlock - A UniformBlock from Mach.UniformBlock
		"""

		self.blocks[uniformBlock.name] = uniformBlock

	def bindUniformBlocks(self):
		" Binds all of the uniform buffer objects from the uniformBlocks"
		for ub in self.blocks:
			self.blocks[ub].autoBind()

	def storeAttributeArray(self, attributes):
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
			attr.setOffset(offset)
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

	def storeElementIndexArray(self, indices):
		"""
		Stores and enables an array of indices for element drawing

		Arguments:
			indices - a list or numpy array of integers
		"""

		indices = numpy.array(indices, dtype=numpy.int32)

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

	def bindImages(self):
		" Binds all user defined images and textures for drawing"
		for texture_id, (name, activeTexture) in self.images.items():
			glActiveTexture(GL_TEXTURE0 + activeTexture)
			glBindTexture(GL_TEXTURE_2D, texture_id)

	def storeTexture(self, name, tex, activeTexture=0, filter=GL_NEAREST):
		"""
		Store a texture (image rendered from a shader) in a sampler2D object

		Arguments:
			name - the name of the uniform variable (string)
			tex - the Texture or DepthTexture that will be attached (Texture, DepthTexture from Mach.Rendered)
			activeTexture - teh offset for the active texture (integer)
			filter - what type of texture filter we want to use (GL_NEAREST for a pixely effect, good for low resolution images
						or GL_LINEAR for blurrier, smoother look)
		"""
		glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
		glBindTexture(GL_TEXTURE_2D, tex.renderedTexture)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filter)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filter)

		self.images[tex.renderedTexture] = (name, activeTexture)

	def storeSampler2D(self, name, path, activeTexture=0, convert="RGBA", filter=GL_NEAREST, internalFormat=GL_RGBA, format=GL_RGBA):
		"""
		Store an image in a sampler2D object

		Arguments:
			name - the name of the uniform variable (string)
			path - the path to the image (string)
			activeTexture - the offset for the active texture (integer)
			filter - what type of texture filter we want to use (GL_NEAREST for a pixely effect, good for low resolution images
						or GL_LINEAR for blurrier, smoother look)
		"""
		im = Image.open(path, mode='r')

		# Some images aren't done in RGBA so we convert it, if the user wants to save RAM or image upload times they can specify their own format or None
		if convert: im = im.convert(convert)

		width, height, image = im.size[0], im.size[1], im.tobytes()

		texture_id = glGenTextures(1)

		glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
		glBindTexture(GL_TEXTURE_2D, texture_id)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filter)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filter)

		glTexImage2D(GL_TEXTURE_2D, 0, internalFormat, width, height, 0, format, GL_UNSIGNED_BYTE, image)

		self.images[texture_id] = (name, activeTexture)

	def bindUniforms(self):
		" Binds all of the object specific uniforms"
		for name in self.uniforms:
			args, func = self.uniforms[name]
			func(*args)

	def storeFloat(self, name, *vals):
		"""
		Store a float or a vector of floats

		Arguments:
			name - the name of the uniform variable (string)
			vals - a set of float arguments
		"""
		if len(vals) > 4:
			print("Cannot store more than four values for " + name)
			return
		loc = self.shader.GetUniformLocation(name)
		self.uniforms[name] = ((loc, *vals), floatFunctions[len(vals)])

	def storeInt(self, name, *vals):
		"""
		Store a int or vector of ints

		Arguments:
			name - the name of the uniform variable (string)
			vals - a set of integer arguments
		"""
		if len(vals) > 4:
			print("Cannot store more than four values for " + name)
			return
		loc = self.shader.GetUniformLocation(name)
		self.uniforms[name] = ((loc, *vals), intFunctions[len(vals)])

	def storeMatrix3(self, name, mat):
		"""
		Store a mat3

		Arguments:
			name - the name of the uniform variable (string)
			mat - a numpy matrix
		"""
		value = numpy.array(mat).flatten()

		loc = self.shader.GetUniformLocation(name)

		self.uniforms[name] = ((loc, (c_float * 9)(*value)), glUniformMatrix3fv)

	def storeMatrix4(self, name, mat):
		"""
		Store a mat4

		Arguments:
			name - the name of the uniform variable (string)
			mat - a numpy matrix
		"""
		value = numpy.array(mat).flatten()

		loc = self.shader.GetUniformLocation(name)
		self.uniforms[name] = ((loc, 1, False, (c_float * 16)(*value)), glUniformMatrix4fv)

"""
A multithreaded alternative for binding images to vertex lists (To be resolved)
"""

vertexLists = []
targets = []
paths = []
activeTextures = []
count = 0

widths = None
heights = None
images = None

def addImageToBeBound(vertexList, target, path, activeTexture=0):
	"""
	Adds image data to a list to be bound to its vertex list in an optimized way
	"""

	global count

	vertexLists.append(vertexList)
	targets.append(target)
	paths.append((count, path))
	activeTextures.append(activeTexture)

	count += 1

def bindImageToVertexList(info):
	"""
	Adds an individual image to a vertex list
	"""

	i = info[0]
	path = info[1]

	im = Image.open(path, mode='r')
	width, height, image = im.size[0], im.size[1], im.tobytes()

	return (i, width, height, image)

def bindImagesToVertexLists(workers=4):
	"""
	Goes through all of the stored images and binds them
	"""

	length = len(vertexLists)

	for path in paths:
		for i, width, height, image in bindImageToVertexList(path):
			texture_id = glGenTextures(1)

			glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
			glBindTexture(GL_TEXTURE_2D, texture_id)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

			glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image)

			vertexLists[i].images[texture_id] = (targets[i], activeTextures[i])
