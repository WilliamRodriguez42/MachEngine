from OpenGL.GL import *
from PIL import Image
import numpy as np

numpy_type_to_gl_type = {
	np.dtype(np.uint8): GL_UNSIGNED_BYTE,
	np.dtype(np.int8): GL_BYTE,
	np.dtype(np.uint16): GL_UNSIGNED_SHORT,
	np.dtype(np.int16): GL_SHORT,
	np.dtype(np.uint32): GL_UNSIGNED_INT,
	np.dtype(np.int32): GL_INT,
	np.dtype(np.float16): GL_HALF_FLOAT,
	np.dtype(np.float32): GL_FLOAT
}

class ImageStorage:
	def __init__(self):
		self.images = {}

	def bind_images(self):
		" Binds all user defined images and textures for drawing"
		for texture_id, (name, active_texture) in self.images.items():
			glActiveTexture(GL_TEXTURE0 + active_texture)
			glBindTexture(GL_TEXTURE_2D, texture_id)

	def store_sampler2D_from_texture(self, name, tex, active_texture=0, filter=GL_NEAREST):
		"""
		Store a texture (image rendered from a shader) in a sampler2D object

		Arguments:
			name - the name of the uniform variable (string)
			tex - the Texture or DepthTexture that will be attached (Texture, DepthTexture from Mach.Rendered)
			active_texture - the offset for the active texture (integer)
			filter - what type of texture filter we want to use (GL_NEAREST, GL_LINEAR, etc)
		"""
		glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
		glBindTexture(GL_TEXTURE_2D, tex.renderedTexture)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filter)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filter)

		self.images[tex.renderedTexture] = (name, active_texture)

	def store_sampler2D_from_path(self, name, path, active_texture=0, convert="RGBA", filter=GL_NEAREST, format=GL_RGBA):
		"""
		Store an image in a sampler2D object

		Arguments:
			name - the name of the uniform variable (string)
			path - the path to the image (string)
			active_texture - the offset for the active texture (integer)
			filter - what type of texture filter we want to use (GL_NEAREST for a pixely effect, good for low resolution images
						or GL_LINEAR for blurrier, smoother look)
		"""
		im = Image.open(path, mode='r')

		# Some images aren't done in RGBA so we convert it, if the user wants to save RAM or image upload times they can specify their own format or None
		if convert: im = im.convert(convert)
		mat = np.array(im)[::-1, :, :]
		self.store_sampler2D_from_numpy(name, mat, active_texture, filter, format)

	def store_sampler2D_from_numpy(self, name, mat, active_texture=0, filter=GL_NEAREST, format=GL_RGBA):
		"""
		Store an image in a sampler2D object. The texture unit is defined by the order in which this texture was added

		Arguments:
			name - the name of the uniform variable (string)
			mat - numpy float matrix with shape [height, width, byte_depth] with values on range 0 to 1
			active_texture - the offset for the active texture (integer)
			filter - what type of texture filter we want to use (GL_NEAREST for a pixely effect, good for low resolution images
						or GL_LINEAR for blurrier, smoother look)
		"""
		width, height, image = mat.shape[1], mat.shape[0], mat.tobytes()

		texture_id = glGenTextures(1)

		glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
		glBindTexture(GL_TEXTURE_2D, texture_id)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filter)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filter)

		glTexImage2D(GL_TEXTURE_2D, 0, format, width, height, 0, format, numpy_type_to_gl_type[mat.dtype], image)

		self.images[texture_id] = (name, active_texture)