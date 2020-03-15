
from ctypes import c_int, byref, create_string_buffer, c_float
from OpenGL.GL import *
from OpenGL.GL.shaders import *
from PIL import Image
import numpy
import struct
import sys
import glob

import mach
# from Mach.Attribute import Attribute
# from Mach.Struct import Struct
# from Mach.UniformBlock import UniformBlock
# from Mach.MachObject import *
import re

class Shader:
	"""
	Manages the creation, usage, and information of variables within a vertex shader and fragment shader

	WARNING!!!!
	This does not support uniform structs! However it does support uniform blocks with structs inside them

	in other words this is not allowed:
		struct HI {
			vec2 var;
		}

		uniform HI foo; // This causes an issue

	However, you can do this:
		struct HI {
			vec3 var;
		}

		uniform BAR {
			HI foo;
		} bar;

	Then to get to foo just use bar.foo

	So it's not that bad, especially because the second option is technically more efficient anyway


	Arguments:
		vert - a string representing the vertex shader source
		geom - a string representing the geometry shader source (optional)
		frag - a string representing the fragment shader source
	"""

	# vert, frag and geom take arrays of source strings
	# the arrays will be concattenated into one string by OpenGL
	def __init__(self, *args):
		if len(args) == 2:
			self.init2(*args)
		else:
			self.init3(*args)

		self.images = {}
		self.uniforms = {}
		self.blocks = {}

	def init2(self, vert, frag):
		" Initialization without geometry source"
		# we are not linked yet
		self.linked = False

		self.VAO = glGenVertexArrays(1)
		self.VBOs = []

		glBindVertexArray(self.VAO)

		try:
			if glob.glob(vert): vert = open(vert, 'r').read()
			if glob.glob(frag): frag = open(frag, 'r').read()

			VERTEX_SHADER = compileShader(vert, GL_VERTEX_SHADER)
			FRAGMENT_SHADER = compileShader(frag, GL_FRAGMENT_SHADER)

			self.shader = glCreateProgram()
			glAttachShader(self.shader, VERTEX_SHADER)
			glAttachShader(self.shader, FRAGMENT_SHADER)

			# attempt to link the program
			self.link()

			# Use this program
			glUseProgram(self.shader)

		except Exception as e:
			decoded_string = bytes(str(e), 'utf-8').decode('unicode_escape')
			decoded_string = bytes(str(decoded_string), 'utf-8').decode('unicode_escape')
			print(decoded_string)
			sys.exit(0)

		# Empty uniform locations
		self.uniformLocations = {}

		self.getUniformBlocksAndStructs(vert, '', frag)

	def init3(self, vert, geom, frag):
		" Initialization with geometry shader"
		# we are not linked yet
		self.linked = False

		self.VAO = glGenVertexArrays(1)
		self.VBOs = []

		glBindVertexArray(self.VAO)

		try:
			if glob.glob(vert): vert = open(vert, 'r').read()
			if glob.glob(geom): geom = open(geom, 'r').read()
			if glob.glob(frag): frag = open(frag, 'r').read()

			VERTEX_SHADER = compileShader(vert, GL_VERTEX_SHADER)
			GEOM_SHADER = compileShader(geom, GL_GEOMETRY_SHADER)
			FRAGMENT_SHADER = compileShader(frag, GL_FRAGMENT_SHADER)

			self.shader = glCreateProgram()
			glAttachShader(self.shader, VERTEX_SHADER)
			glAttachShader(self.shader, GEOM_SHADER)
			glAttachShader(self.shader, FRAGMENT_SHADER)

			# attempt to link the program
			self.link()

			# Use this program
			glUseProgram(self.shader)

		except Exception as e:
			decoded_string = bytes(str(e), 'utf-8').decode('unicode_escape')
			decoded_string = bytes(str(decoded_string), 'utf-8').decode('unicode_escape')
			print(decoded_string)
			sys.exit(0)

		# Empty uniform locations
		self.uniformLocations = {}

		self.getUniformBlocksAndStructs(vert, geom, frag)

	def getUniformBlocksAndStructs(self, vert, geom, frag):
		# Loop through the vertex, geometry, and fragment source and find all of the uniform blocks
		sourceArray = (vert + geom + frag)

		# Remove all of the semicolons
		sourceArray = sourceArray.replace(';', '')

		# Put a space before and after any opening or closing brackets
		sourceArray = sourceArray.replace('{', ' { ').replace(' }', ' }')

		# Split our source string by whitespace
		sourceArray = sourceArray.split()

		# Remove any witespace before an array bracket
		for i in range(1, len(sourceArray)):
			if sourceArray[i] == '[':
				sourceArray[i-1] += '[' + sourceArray[i+1]
				sourceArray[i] = ''
				sourceArray[i+1] = ''
			elif sourceArray[i] == ']':
				j = i
				while(sourceArray[j-1] == ''):
					j -= 1

				sourceArray[j-1] += ']'
				sourceArray[i] = ''


		self.dataTypeToByteCount = {
			"vec2" : 8,
			"vec3" : 12,
			"vec4" : 16,
			"mat3" : 48,
			"mat4" : 64,
			"float": 4,
			"int"  : 4,
			"bool" : 4
		}

		self.dataTypeToArrayByteCount = {
			"vec2" : 16,
			"vec3" : 16,
			"vec4" : 16,
			"mat3" : 48,
			"mat4" : 64,
			"float": 16,
			"int"  : 16,
			"bool" : 16
		}

		test = (vert + geom + frag)
		variableNameSearch = re.compile(r'(bool|float|int|vec.|ivec.|mat.|imat.)\s+(\S*?)\s*(?:\[\s*([0-9]*)\s*\])*\s*?;')

		self.glslStructs = {}

		currentOffsetCount = 0
		lastByteCount = 0
		lastArrayByteCount = 0

		structSearch = re.compile(r'struct\s+(\S+)\s*{([\s|\S]+?)}')
		structs = structSearch.finditer(test)
		for s in structs:
			currentStruct = s.group(1)
			self.glslStructs[currentStruct] = {}

			varNames = variableNameSearch.finditer(s.group(2))

			for v in varNames:
				vType = v.group(1)
				vName = v.group(2)

				lastByteCount = self.dataTypeToByteCount[vType]

				if v.group(3):
					# The variable is an array
					num = int(v.group(3))

					arrayDataSize = self.dataTypeToArrayByteCount[vType]
					lastByteCount = int(num * arrayDataSize)
					lastArrayByteCount = lastByteCount

					self.glslStructs[currentStruct][vName] = (currentOffsetCount, lastByteCount)
					currentOffsetCount += lastByteCount

				else:
					# The variable is not an array

					# Map the variable to its data offset
					lastSectorSize = currentOffsetCount % 16

					# If the variable can fit within one sector, find if it can fit in the last sector
					if (lastByteCount <= 16 and lastSectorSize + lastByteCount > 16):
						# We don't have enought room in this sector to fit this item, throw it into a new sector
						currentOffsetCount += 16 - lastSectorSize
					elif (lastByteCount > 16):
						# The object is too big to fit in a partial sector, so fit it into the first empty sector
						if lastSectorSize != 0:
							currentOffsetCount += 16 - lastSectorSize

					self.glslStructs[currentStruct][vName] = (currentOffsetCount, lastByteCount)
					currentOffsetCount += lastByteCount

			# Pad currentOffsetCount
			lastSectorSize = currentOffsetCount % 16
			if (lastSectorSize != 0):
				currentOffsetCount += 16 - lastSectorSize

			self.dataTypeToByteCount[currentStruct] = currentOffsetCount
			self.dataTypeToArrayByteCount[currentStruct] = currentOffsetCount

			currentOffsetCount = 0
			lastByteCount = 0
			lastArrayByteCount = 0

		self._uniformBlocks = {}
		self.uniformBlockSizes = {}
		self.uniformIndexes = {}
		currentIndex = 0

		# Structs can be used within uniform blocks so we have to add them to the variable search
		structString = ''
		for d in self.glslStructs:
			structString += '|' + d
		variableNameSearch = re.compile(r'(bool|float|int|vec.|ivec.|mat.|imat.' + structString + r')\s+(\S*?)\s*(?:\[\s*([0-9]*)\s*\])*\s*?;')

		uniformSearch = re.compile(r'uniform\s+(\S+)\s*{([\s|\S]+?)}')
		uniforms = uniformSearch.finditer(test)

		for u in uniforms:
			currentUniformBlock = u.group(1)
			self._uniformBlocks[currentUniformBlock] = {}
			self.uniformIndexes[currentUniformBlock] = currentIndex
			currentIndex += 1

			varNames = variableNameSearch.finditer(u.group(2))

			for v in varNames:
				vType = v.group(1)
				vName = v.group(2)

				lastByteCount = self.dataTypeToByteCount[vType]

				if v.group(3):
					# The variable is an array
					num = int(v.group(3))

					# Get the number of items in the array
					arrayDataSize = self.dataTypeToArrayByteCount[vType]
					lastByteCount = int(num * arrayDataSize)

					self._uniformBlocks[currentUniformBlock][vName] = (currentOffsetCount, lastByteCount)
					currentOffsetCount += lastByteCount

				else:
					# The variable is not an array

					# Map the variable to its data offset
					lastSectorSize = currentOffsetCount % 16

					# If the variable can fit within one sector, find if it can fit in the last sector
					if (lastByteCount <= 16 and lastSectorSize + lastByteCount > 16):
						# We don't have enought room in this sector to fit this item, throw it into a new sector
						currentOffsetCount += 16 - lastSectorSize
					elif (lastByteCount > 16):
						# The object is too big to fit in a partial sector, so fit it into the first empty sector
						if lastSectorSize != 0:
							currentOffsetCount += 16 - lastSectorSize

					self._uniformBlocks[currentUniformBlock][vName] = (currentOffsetCount, lastByteCount)
					currentOffsetCount += lastByteCount

			self.uniformBlockSizes[currentUniformBlock] = currentOffsetCount
			currentOffsetCount = 0
			lastByteCount = 0

	def GetUniformIndex(self, name):
		" Gets the order which this uniform block was created (0 if it was the first uniform block created, 1 if the second and so on)"
		return self.uniformIndexes[name]

	def GetUniformLocation(self, name):
		" Get the location of a uniform variable (name - the name of the uniform variable in glsl)"
		if (name not in self.uniformLocations):
			self.uniformLocations[name] = glGetUniformLocation(self.shader, name)
		return self.uniformLocations[name]

	def GetBlockUniformInfo(self, blockname, name):
		" Get the offset and size of a variable within a uniform block (blockname - the name of the uniform block the variable is stored in, name - the name of the variable)"
		return self._uniformBlocks[blockname][name]

	def GetStructUniformInfo(self, structname, name):
		" Get the offset and size of a uniform struct"
		return self.glslStructs[structname][name]

	def GetStructSize(self, structname):
		" Get the size of a uniform struct (structname - the name of the struct object (not the variable name))"
		return self.dataTypeToByteCount[structname]

	def GetUniformBlockSize(self, blockname):
		" Get the size of a uniform block (blockname - the name of the uniform block)"
		return self.uniformBlockSizes[blockname]

	def GetBlockLocation(self, blockname):
		" Get the location of a uniform block (blockname - the name of the uniform block)"
		if (blockname not in self.uniformLocations):
			self.uniformLocations[blockname] = glGetUniformBlockIndex(self.shader, blockname)
		return self.uniformLocations[blockname]

	def createNewMachObject(self, drawType=GL_TRIANGLES):
		" A shortcut to create a new drawable object"
		obj = mach.MachObject(self, drawType)
		return obj

	def bind(self, skipImages=False, skipUniforms=False, skipBlocks=False):
		" Bind the shader"
		# bind the program
		glUseProgram(self.shader)
		glBindVertexArray(self.VAO)

		# Bind any images that
		if not skipImages:		self.bindImages()
		if not skipUniforms:	self.bindUniforms()
		if not skipBlocks:		self.bindUniformBlocks()

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
		loc = self.GetUniformLocation(name)
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
		loc = self.GetUniformLocation(name)
		self.uniforms[name] = ((loc, *vals), intFunctions[len(vals)])

	def storeMatrix3(self, name, mat):
		"""
		Store a mat3

		Arguments:
			name - the name of the uniform variable (string)
			mat - a numpy matrix
		"""
		value = numpy.array(mat).flatten()

		loc = self.GetUniformLocation(name)
		self.uniforms[name] = ((loc, (c_float * 9)(*value)), glUniformMatrix3fv)

	def storeMatrix4(self, name, mat):
		"""
		Store a mat4

		Arguments:
			name - the name of the uniform variable (string)
			mat - a numpy matrix
		"""
		value = numpy.array(mat).flatten()

		loc = self.GetUniformLocation(name)
		self.uniforms[name] = ((loc, 1, False, (c_float * 16)(*value)), glUniformMatrix4fv)

	def link(self):
		" Attempt to link the geometry, vertex, and fragment shaders"
		# link the program
		glLinkProgram(self.shader)

		temp = c_int(0)
		# retrieve the link status
		glGetProgramiv(self.shader, GL_LINK_STATUS, byref(temp))

		# if linking failed, print the log
		if not temp:
			#	retrieve the log length
			glGetProgramiv(self.shader, GL_INFO_LOG_LENGTH, byref(temp))
			# create a buffer for the log
			buffer = create_string_buffer(temp.value)
			# retrieve the log text
			print(glGetProgramInfoLog(self.shader).decode('unicode_escape'))
			# print the log to the console
			print(temp.value)
			print(".........................")
		else:
			# all is well, so we are linked
			self.linked = True
