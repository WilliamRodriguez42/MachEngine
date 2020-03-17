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
VIDEOMOVED = 10
MOUSEBUTTONDOUBLECLICKED = 11
MOUSEWHEEL = 12
FOCUSIN = 13
FOCUSOUT = 14
HIDE = 15
SHOW = 16
TABLET = 17

class Event:
	def __init__(
		self,
		type,
		qt_event,
		size = None,
		key = None,
		pos = None,
		button = None,
		angle_delta = None,
		pixel_delta = None
	):
		self.type = type
		self.qt_event = qt_event
		self.size = None
		self.key = key
		self.pos = None
		self.button = button
		self.angle_delta = angle_delta
		self.pixel_delta = pixel_delta

		if size is not None: self.size = np.array(size, dtype=np.int)
		if pos is not None: self.pos = np.array(pos, dtype=np.int)

class EventManager:
	def __init__(self):
		self.event_queue = []
		self.max_num_events = 1000

	def queue_event(self, event):
		self.event_queue.append(event)

		if len(self.event_queue) > self.max_num_events:
			del self.event_queue[0]

	def get(self):
		result = self.event_queue
		self.event_queue = []
		return result