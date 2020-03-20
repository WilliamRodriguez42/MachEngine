from OpenGL.GL import *
from PIL import Image
import numpy
import mach

class MachObject(mach.UniformBlockStorage, mach.UniformStorage, mach.ImageStorage, mach.AttributeStorage):
	"""
	Organizes the usage of individual uniforms and AttributeObjects,

	Arguments:
		shader - the shader object this object is bound to
		draw_type - How the vertices are going to be drawn
	"""
	def __init__(self, shader, draw_type=GL_TRIANGLES):
		mach.UniformBlockStorage.__init__(self)
		mach.UniformStorage.__init__(self)
		mach.ImageStorage.__init__(self)
		mach.AttributeStorage.__init__(self)

		self.draw_type = draw_type
		self.shader = shader

	def bind(self, skip_attributes=False, skip_images=False, skip_uniforms=False, skip_blocks=False):
		if not skip_attributes:	self.bind_attributes()
		if not skip_images:		self.bind_images()
		if not skip_uniforms:	self.bind_uniforms()
		if not skip_blocks:		self.bind_uniform_blocks()

	def draw(self):
		" Draw our object"
		if (self.IBO is None):
			glDrawArrays(self.draw_type, 0, self.count)
		else:
			glDrawElements(self.draw_type, self.count, GL_UNSIGNED_INT, None)

	# Passthrough info functions to shader
	def get_uniform_index(self, name):
		return self.shader.get_uniform_index(name)
	def get_uniform_location(self, name):
		return self.shader.get_uniform_location(name)
	def get_block_uniform_info(self, blockname, name):
		return self.shader.get_uniform_block_size(blockname, name)
	def get_struct_uniform_info(self, structname, name):
		return self.shader.get_struct_uniform_info(structname, name)
	def get_struct_size(self, structname):
		return self.shader.get_struct_size(blockname)
	def get_uniform_block_size(self, blockname):
		return self.shader.get_uniform_block_size(blockname)
	def get_block_location(self, blockname):
		return self.shader.get_block_location(blockname)

vertex_lists = []
targets = []
paths = []
active_textures = []
count = 0

widths = None
heights = None
images = None

def add_image_to_be_bound(vertex_list, target, path, active_texture=0):
	"""
	Adds image data to a list to be bound to its vertex list
	"""

	global count

	vertex_lists.append(vertex_list)
	targets.append(target)
	paths.append((count, path))
	active_textures.append(active_texture)

	count += 1

def bind_image_to_vertex_list(info):
	"""
	Adds an individual image to a vertex list
	"""

	i = info[0]
	path = info[1]

	im = Image.open(path, mode='r')
	width, height, image = im.size[0], im.size[1], im.tobytes()

	return (i, width, height, image)

def bind_images_to_vertex_lists(workers=4):
	"""
	Goes through all of the stored images and binds them
	"""

	length = len(vertex_lists)

	for path in paths:
		for i, width, height, image in bind_image_to_vertex_list(path):
			texture_id = glGenTextures(1)

			glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
			glBindTexture(GL_TEXTURE_2D, texture_id)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

			glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)

			vertex_lists[i].images[texture_id] = (targets[i], active_textures[i])
