
from ctypes import c_int, byref, create_string_buffer
from OpenGL.GL import *
from OpenGL.GL.shaders import *
import sys
import re

import mach

class Shader(mach.UniformBlockStorage, mach.UniformStorage, mach.ImageStorage):
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
		mach.UniformBlockStorage.__init__(self)
		mach.UniformStorage.__init__(self)
		mach.ImageStorage.__init__(self)

		if len(args) == 2:
			self.install_shaders(args[0], args[1])
		else:
			self.install_shaders(args[0], args[2], geom=args[1])

	def install_shaders(self, vert, frag, geom=None):
		" Initialization with geometry shader"
		# we are not linked yet
		self.linked = False

		self.VAO = glGenVertexArrays(1)

		glBindVertexArray(self.VAO)

		try:
			vert = open(vert, 'r').read()
			if geom is not None: geom = open(geom, 'r').read()
			frag = open(frag, 'r').read()

			VERTEX_SHADER = compileShader(vert, GL_VERTEX_SHADER)
			if geom is not None: GEOM_SHADER = compileShader(geom, GL_GEOMETRY_SHADER)
			FRAGMENT_SHADER = compileShader(frag, GL_FRAGMENT_SHADER)

			self.shader = glCreateProgram()
			glAttachShader(self.shader, VERTEX_SHADER)
			if geom is not None: glAttachShader(self.shader, GEOM_SHADER)
			glAttachShader(self.shader, FRAGMENT_SHADER)

			# attempt to link the program
			self.link()

			# Use this program
			glUseProgram(self.shader)

		except ShaderCompilationError as e:
			compile_failure_string = e.args[0].replace("b'", '\n')[:-1]
			print(bytes(compile_failure_string, 'utf-8').decode('unicode_escape'), file=sys.stderr)
			# for item in e.args[1]:
			# 	print(item.decode('unicode_escape'))
			print(e.args[2], file=sys.stderr)
			sys.exit(1)

		# Empty uniform locations
		self.uniform_locations = {}

		self.get_uniform_blocks_and_structs(vert, geom, frag)

	def get_uniform_blocks_and_structs(self, vert, geom, frag):
		# Loop through the vertex, geometry, and fragment source and find all of the uniform blocks
		if geom is not None: source_content = vert + geom + frag
		else: source_content = vert + frag
		source_content_copy = str(source_content)

		# Remove all of the semicolons
		source_content = source_content.replace(';', '')

		# Put a space before and after any opening or closing brackets
		source_content = source_content.replace('{', ' { ').replace(' }', ' }')

		# Split our source string by whitespace
		source_content = source_content.split()

		# Remove any witespace before an array bracket
		for i in range(1, len(source_content)):
			if source_content[i] == '[':
				source_content[i-1] += '[' + source_content[i+1]
				source_content[i] = ''
				source_content[i+1] = ''
			elif source_content[i] == ']':
				j = i
				while(source_content[j-1] == ''):
					j -= 1

				source_content[j-1] += ']'
				source_content[i] = ''

		self.data_type_to_byte_count = {
			"vec2" : 8,
			"vec3" : 12,
			"vec4" : 16,
			"mat3" : 48,
			"mat4" : 64,
			"float": 4,
			"int"  : 4,
			"bool" : 4
		} # Number of bytes for each data type

		self.data_type_to_array_byte_count = {
			"vec2" : 16,
			"vec3" : 16,
			"vec4" : 16,
			"mat3" : 48,
			"mat4" : 64,
			"float": 16,
			"int"  : 16,
			"bool" : 16
		} # Number of bytes for each data type when inside an array

		variable_name_search = re.compile(r'(bool|float|int|vec.|ivec.|mat.|imat.)\s+(\S*?)\s*(?:\[\s*([0-9]*)\s*\])*\s*?;')

		self.glsl_structs = {}

		current_offset_count = 0
		last_byte_count = 0
		last_array_byte_count = 0

		struct_search = re.compile(r'struct\s+(\S+)\s*{([\s|\S]+?)}')
		structs = struct_search.finditer(source_content_copy)
		for s in structs:
			create_struct = s.group(1)
			self.glsl_structs[create_struct] = {}

			variable_name_matches = variable_name_search.finditer(s.group(2))

			for match in variable_name_matches:
				variable_type = match.group(1)
				variable_name = match.group(2)

				last_byte_count = self.data_type_to_byte_count[variable_type]

				if match.group(3):
					# The variable is an array
					num = int(match.group(3))

					array_data_size = self.data_type_to_array_byte_count[variable_type]
					last_byte_count = int(num * array_data_size)
					last_array_byte_count = last_byte_count

					self.glsl_structs[create_struct][variable_name] = (current_offset_count, last_byte_count)
					current_offset_count += last_byte_count

				else:
					# The variable is not an array

					# Map the variable to its data offset
					last_sector_size = current_offset_count % 16

					# If the variable can fit within one sector, find if it can fit in the last sector
					if (last_byte_count <= 16 and last_sector_size + last_byte_count > 16):
						# We don't have enought room in this sector to fit this item, throw it into a new sector
						current_offset_count += 16 - last_sector_size
					elif (last_byte_count > 16):
						# The object is too big to fit in a partial sector, so fit it into the first empty sector
						if last_sector_size != 0:
							current_offset_count += 16 - last_sector_size

					self.glsl_structs[create_struct][variable_name] = (current_offset_count, last_byte_count)
					current_offset_count += last_byte_count

			# Pad current_offset_count
			last_sector_size = current_offset_count % 16
			if (last_sector_size != 0):
				current_offset_count += 16 - last_sector_size

			self.data_type_to_byte_count[create_struct] = current_offset_count
			self.data_type_to_array_byte_count[create_struct] = current_offset_count

			current_offset_count = 0
			last_byte_count = 0
			last_array_byte_count = 0

		self._uniform_blocks = {}
		self.uniform_block_sizes = {}
		self.uniform_indices = {}
		current_index = 0

		# Structs can be used within uniform blocks so we have to add them to the variable search
		struct_string = ''
		for d in self.glsl_structs:
			struct_string += '|' + d
		variable_name_search = re.compile(r'(bool|float|int|vec.|ivec.|mat.|imat.' + struct_string + r')\s+(\S*?)\s*(?:\[\s*([0-9]*)\s*\])*\s*?;')

		uniformSearch = re.compile(r'uniform\s+(\S+)\s*{([\s|\S]+?)}')
		uniforms = uniformSearch.finditer(source_content_copy)

		for u in uniforms:
			current_uniform_block = u.group(1)
			self._uniform_blocks[current_uniform_block] = {}
			self.uniform_indices[current_uniform_block] = current_index
			current_index += 1

			variable_name_matches = variable_name_search.finditer(u.group(2))

			for match in variable_name_matches:
				variable_type = match.group(1)
				variable_name = match.group(2)

				last_byte_count = self.data_type_to_byte_count[variable_type]

				if match.group(3):
					# The variable is an array
					num = int(match.group(3))

					# Get the number of items in the array
					array_data_size = self.data_type_to_array_byte_count[variable_type]
					last_byte_count = int(num * array_data_size)

					self._uniform_blocks[current_uniform_block][variable_name] = (current_offset_count, last_byte_count)
					current_offset_count += last_byte_count

				else:
					# The variable is not an array

					# Map the variable to its data offset
					last_sector_size = current_offset_count % 16

					# If the variable can fit within one sector, find if it can fit in the last sector
					if (last_byte_count <= 16 and last_sector_size + last_byte_count > 16):
						# We don't have enought room in this sector to fit this item, throw it into a new sector
						current_offset_count += 16 - last_sector_size
					elif (last_byte_count > 16):
						# The object is too big to fit in a partial sector, so fit it into the first empty sector
						if last_sector_size != 0:
							current_offset_count += 16 - last_sector_size

					self._uniform_blocks[current_uniform_block][variable_name] = (current_offset_count, last_byte_count)
					current_offset_count += last_byte_count

			self.uniform_block_sizes[current_uniform_block] = current_offset_count
			current_offset_count = 0
			last_byte_count = 0

	def get_uniform_index(self, name):
		" Gets the order which this uniform block was created (0 if it was the first uniform block created, 1 if the second and so on)"
		return self.uniform_indices[name]

	def get_uniform_location(self, name):
		" Get the location of a uniform variable (name - the name of the uniform variable in glsl)"
		if (name not in self.uniform_locations):
			self.uniform_locations[name] = glGetUniformLocation(self.shader, name)
		return self.uniform_locations[name]

	def get_block_uniform_info(self, blockname, name):
		" Get the offset and size of a variable within a uniform block (blockname - the name of the uniform block the variable is stored in, name - the name of the variable)"
		return self._uniform_blocks[blockname][name]

	def get_struct_uniform_info(self, structname, name):
		" Get the offset and size of a uniform struct"
		return self.glsl_structs[structname][name]

	def get_struct_size(self, structname):
		" Get the size of a uniform struct (structname - the name of the struct object (not the variable name))"
		return self.data_type_to_byte_count[structname]

	def get_uniform_block_size(self, blockname):
		" Get the size of a uniform block (blockname - the name of the uniform block)"
		return self.uniform_block_sizes[blockname]

	def get_block_location(self, blockname):
		" Get the location of a uniform block (blockname - the name of the uniform block)"
		if (blockname not in self.uniform_locations):
			self.uniform_locations[blockname] = glGetUniformBlockIndex(self.shader, blockname)
		return self.uniform_locations[blockname]

	def create_new_mach_object(self, drawType=GL_TRIANGLES):
		" A shortcut to create a new drawable object"
		obj = mach.MachObject(self, drawType)
		return obj

	def bind(self, skipImages=False, skipUniforms=False, skipBlocks=False):
		" Bind the shader"
		# bind the program
		glUseProgram(self.shader)
		glBindVertexArray(self.VAO)

		# Bind any images that
		if not skipImages:		self.bind_images()
		if not skipUniforms:	self.bind_uniforms()
		if not skipBlocks:		self.bind_uniform_blocks()

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
