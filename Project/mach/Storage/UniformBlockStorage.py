from OpenGL.GL import *

class UniformBlockStorage:
	def __init__(self):
		self.blocks = {}

	def bind_uniform_blocks(self):
		" Binds all of the uniform buffer objects from the uniformBlocks"
		for ub in self.blocks:
			self.blocks[ub].autoBind()

	def store_uniform_block(self, uniform_block):
		"""
		Stores a uniform_block to be bound

		Arguments:
			uniform_block - A UniformBlock from Mach.UniformBlock
		"""

		self.blocks[uniform_block.name] = uniform_block