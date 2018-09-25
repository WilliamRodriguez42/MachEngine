from inputs import devices

class Controller:
    deadzone = 5000
    max_zone = 32768

    lx = 0
    ly = 0
    rx = 0
    ry = 0

    south = 0
    north = 0
    east = 0
    west = 0

    dleft = 0
    dright = 0
    dup = 0
    ddown = 0

    start = 0
    select = 0

    thumbl = 0
    thumbr = 0

    bumperl = 0
    bumperr = 0

    triggerl = 0
    triggerr = 0

    def __init__(self, controller_num):
        self.controller_num = controller_num

    def get_events(self):
        events = devices.gamepads[self.controller_num].read()
        for e in events:
            code = e.code
            (self.callback[code])(self, e.state)

    def remove_deadzone(self, v):
        if abs(v) > self.deadzone:
            return v / self.max_zone
        return 0

    def _rx(self, v):
        self.rx = self.remove_deadzone(v)

    def _ry(self, v):
        self.ry = self.remove_deadzone(v)

    def _ly(self, v):
        self.ly = self.remove_deadzone(v)

    def _lx(self, v):
        self.lx = self.remove_deadzone(v)

    def hit_south(self, v):
        self.south = v

    def hit_north(self, v):
        self.north = v

    def hit_east(self, v):
        self.east = v

    def hit_west(self, v):
        self.west = v

    def hatx(self, v):
        self.dleft = self.dright = v
        if v > 0:
            self.dleft = 0
        elif v < 0:
            self.dright = 0

    def haty(self, v):
        self.dup = self.ddown = v
        if v > 0:
            self.dup = 0
        elif v < 0:
            self.ddown = 0

    def _start(self, v):
        self.start = v

    def _select(self, v):
        self.select = v

    def _thumbl(self, v):
        self.thumbl = v

    def _thumbr(self, v):
        self.thumbr = v

    def _tl(self, v):
        self.bumpl = v

    def _tr(self, v):
        self.bumpr = v

    def _lz(self, v):
        self.triggerl = v / 255

    def _rz(self, v):
        self.triggerr = v / 255

    def buttonPressEvent(self, button):
        print(button)

    def buttonReleaseEvet(self, button):
        pass

    callback = {
        'ABS_RX': _rx,
        'ABS_RY': _ry,
        'ABS_X': _lx,
        'ABS_Y': _ly,
        'BTN_SOUTH': hit_south,
        'BTN_NORTH': hit_north,
        'BTN_EAST': hit_east,
        'BTN_WEST': hit_west,
        'ABS_HAT0X': hatx,
        'ABS_HAT0Y': haty,
        'SYN_REPORT': lambda x, y: x,
        'BTN_START': _start,
        'BTN_SELECT': _select,
        'BTN_THUMBL': _thumbl,
        'BTN_THUMBR': _thumbr,
        'BTN_TL': _tl,
        'BTN_TR': _tr,
        'ABS_Z' : _lz,
        'ABS_RZ': _rz
    }

if __name__ == '__main__':
    c = Controller(0)
    while True:
        c.get_events()
        print(c.north, c.east, c.south, c.west)
