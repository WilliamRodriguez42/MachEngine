import mach
import numpy as np
from PyQt5.QtCore import Qt

# Copy Qt Key_ declarations
_qt_locals = dir(Qt)
_qt_key_locals = [(k, Qt.__dict__[k]) for k in _qt_locals if k.startswith('Key_')]
_globals = globals()
_globals.update(_qt_key_locals)

# Event types
QUIT = 0
ACTIVEEVENT = 1
KEYDOWN = 2
KEYUP = 3
MOUSEMOTION = 4
MOUSEBUTTONUP = 5
MOUSEBUTTONDOWN = 6
VIDEORESIZE = 7
VIDEOEXPOSE = 8
USEREVENT = 9

class Event:
	def __init__(
		self, 
		type, 
		size = None,
		key = None,
		pos = None
	):
		self.type = type
		self.size = None
		self.key = 0
		self.pos = None

		if size: self.size = np.array(size, dtype=np.int)
		if pos: self.pos = np.array(pos, dtype=np.int)

class EventManager:
	def __init__(self):
		self.event_queue = []

	def queue_event(self, event):
		self.event_queue.append(event)

	def get(self):
		result = self.event_queue
		self.event_queue = []
		return result