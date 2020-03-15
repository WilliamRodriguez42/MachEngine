from lxml import etree
import numpy as np

class Sprite:
	def __init__(self, n, x, y, w, h, px, py, pw, ph, r):
		self.n = n
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.px = px
		self.py = py
		self.pw = pw
		self.ph = ph
		self.r = r

	def recalcCoords(self, coords):
		xvals = [coords[i] for i in range(0, len(coords), 2)]
		yvals = [coords[i] for i in range(1, len(coords), 2)]

		xvals = np.array(xvals, dtype=np.float32)
		yvals = np.array(yvals, dtype=np.float32)

		xvals *= self.w
		xvals += self.x

		yvals *= self.h
		yvals += self.y

		result = []
		for i in range(len(xvals)):
			result.append(xvals[i])
			result.append(yvals[i])

		return result

	def __repr__(self):
		return str((self.x, self.y, self.w, self.h))

def toFloat(s):
	if s is not None:
		return float(s)
	return 0

def toInt(s):
	if s is not None:
		return int(s)
	return 0

def parse(filename):
	sprites = {}

	tree = etree.parse(filename)

	TA = tree.xpath('/TextureAtlas')[0]
	width = toFloat(TA.get('width'))
	height = toFloat(TA.get('height'))

	for n, sprite in enumerate(tree.xpath('/TextureAtlas/sprite')):
		x = toFloat(sprite.get('x')) / width
		y = toFloat(sprite.get('y')) / height
		w = toFloat(sprite.get('w')) / width
		h = toFloat(sprite.get('h')) / height

		px = toInt(sprite.get('x'))
		py = toInt(sprite.get('y'))
		pw = toInt(sprite.get('w'))
		ph = toInt(sprite.get('h'))

		r = toFloat(sprite.get('r'))

		sprites[n] = Sprite(n, x, y, w, h, px, py, pw, ph, r)

	return sprites
