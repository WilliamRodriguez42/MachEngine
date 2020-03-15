import numpy as np
from PIL import Image

# PyOpenGL imports
from OpenGL.GL import *
from OpenGL.GLUT import *

possibleErrors = {
	GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT : 'Incomplete Attachment',
	# GL_FRAMEBUFFER_INCOMPLETE_DIMENSIONS : 'Incomplete Dimensions',
	GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT : 'Incomplete Missing Attachment',
	GL_FRAMEBUFFER_UNSUPPORTED : 'Unsupported',
	GL_FRAMEBUFFER_COMPLETE : 'Complete'
}

class Texture:
	"""
	Easily allows a user to render off-screen to a texture of defined size, or
	even save or edit that texture (Without multithreading or multisampling, that you can
	do yourself)

	Arguments:
		width - the width of the desired output image (integer)
		height - the height of the desired output image (integer)
		attachment - where the image should be attached (integer) (This corresponds to the layout(location = 0)
							from the output color value in the fragment shader)
	"""
	def __init__(self, width, height, attachment=0):
		self.width = width
		self.height = height

		self.buf = GLuint(0)
		glGenFramebuffers(1, self.buf)
		glBindFramebuffer(GL_FRAMEBUFFER, self.buf)

		self.renderedTexture = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, self.renderedTexture)
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)

		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

		glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0 + attachment, self.renderedTexture, 0)

		state = glCheckFramebufferStatus(GL_FRAMEBUFFER)
		if state != GL_FRAMEBUFFER_COMPLETE:
			print('Framebuffer state: ' + possibleErrors[state])

	def bind(self):
		" Binds this texture so that it may be rendered to"
		glBindFramebuffer(GL_FRAMEBUFFER, self.buf)
		glViewport(0, 0, self.width, self.height)

	def save(self, path):
		"""
		A quick way to save the image to your file system, good for screen shots

		Arguments:
			path - the file location of the output file (string)
		"""
		img = self.toImage()
		img.save(path)

	def toImage(self):
		" Converts this texture to a PIL.Image that can be modified"
		a = glReadPixels( 0, 0, self.width, self.height, GL_RGBA, GL_UNSIGNED_BYTE)
		arr = np.array(list(a), dtype=np.uint8)
		arr = arr.reshape(self.width, self.height, 4)

		img = Image.fromarray(arr)
		return img

class DepthTexture:
	"""
	Easily allows a user to render the depth of a scene to a texture of defined size, or
	even save or edit that texture (Without multithreading or multisampling, that you can
	do yourself)

	Arguments:
		width - the width of the desired output image (integer)
		height - the height of the desired output image (integer)
	"""
	def __init__(self, width, height):
		self.width = width
		self.height = height

		self.depthrenderbuffer = glGenRenderbuffers(1)
		glBindRenderbuffer(GL_RENDERBUFFER, self.depthrenderbuffer)
		glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, width, height)
		glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, self.depthrenderbuffer)

		self.renderedTexture = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, self.renderedTexture)
		glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT24, self.width, self.height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)

		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

		glFramebufferTexture(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, self.renderedTexture, 0)

		state = glCheckFramebufferStatus(GL_FRAMEBUFFER)
		if state != GL_FRAMEBUFFER_COMPLETE:
			print('Depthbuffer state: ' + possibleErrors[state])

	def bind(self):
		" Binds this texture so that it may be rendered to"
		glBindRenderbuffer(GL_RENDERBUFFER, self.depthrenderbuffer)
		glViewport(0, 0, self.width, self.height)

	def save(self, path):
		"""
		A quick way to save the image to your file system, good for screen shots

		Arguments:
			path - the file location of the output file (string)
		"""
		img = self.toImage()
		img.save(path)

	def toImage(self):
		" Converts this texture to a PIL.Image that can be modified"
		a = glReadPixels(0, 0, self.width, self.height, GL_DEPTH_COMPONENT, GL_UNSIGNED_BYTE)
		arr = np.array(list(a), dtype=np.uint8).repeat(3)
		arr = arr.reshape(self.width, self.height, 3)

		img = Image.fromarray(arr)
		return img
