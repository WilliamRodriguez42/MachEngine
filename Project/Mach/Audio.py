import libaudioverse
import inspect
import time
import numpy as np
from Mach.Delay import add_delay_event, init, close

libaudioverse.initialize()

server = libaudioverse.Server()
server.set_output_device("default")

# The speed of sound in km/s
sps = 0.343

# This library can't handle sounds generated from objects moving faster than
# the speed of sound, so here we specify the fastest and slowest frequency multiplier
max_rate = 100
min_rate = 0.01

# Default audio multiplier
# Changes how the audio drops over distance
mult = 0.5

# Default maximum multiplier
# To prevent the user from going def, we add a maximum multiplier for the audio
max_mult = 2

class AudioListener(libaudioverse.EnvironmentNode):
    def __init__(self, reverb=True):
        super().__init__(server, "default")

        self.panning_strategy = libaudioverse.PanningStrategies.hrtf
        self.output_channels = 2
        self.connect(0, server)

        self.location = [0, 0, 0]
        self.velocity = [0, 0, 0]

        if reverb:
            """
            Adds a reverb node, which makes the audio more realistic.
            A reverb node is added by default, with default properties,
            to change these properties, modify the variables
                self.reverb.density
                self.reverb.t60

            More values can be changed, but these two are the most common,
            for more information about how reverb can be used, visit
            https://libaudioverse.github.io/libaudioverse/docs/branches/master/libaudioverse_manual.html
            """
            self.reverb = libaudioverse.FdnReverbNode(server)
            send = self.add_effect_send(channels = 4, is_reverb=True, connect_by_default=True)
            self.connect(0, self.reverb, 0)
            self.reverb.connect(0, server)

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, position):
        self._location = np.array(position, dtype=np.float32)
        self.position = self._location

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, velocity):
        self._velocity = np.array(velocity, dtype=np.float32)

    def move(self, dt):
        self.location += self.velocity * dt

class AudioBuffer(libaudioverse.Buffer):
    """
    Contains a sound that can be played
    """
    def __init__(self, filepath):
        super().__init__(server)
        self.load_from_file(filepath)


"""
According to the libaudioverse documentation, these guys are soft-linked
So to delete them all you have to do is de-reference them
"""
class AudioSource(libaudioverse.SourceNode):
    """
    Represents an audio source

    The listener is a reference to an AudioListener object
    The buffer is the audio that we will be playing
    If use_delay is true, then pause and play actions,
        as well as reset and set_audio_position,
        will be delayed according to the speed of sound
    """
    def __init__(self, listener, buffer, use_delay = True):
        super().__init__(server, listener)

        self.n = libaudioverse.BufferNode(server)
        self.l = listener
        self.n.connect(0, self, 0)
        self.n.state = libaudioverse.NodeStates.paused

        self.buffer = buffer

        self.location = [0, 0, 0]
        self.velocity = [0, 0, 0]

        # Changes how audio drops off over distance
        self.mult = mult

        # Prevents the speakers from clipping if the audio source
        # Is right in the user's ear
        self.max_mult = max_mult

        self.use_delay = use_delay

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, location):
        self._location = np.array(location, dtype=np.float32)
        self.position = self._location / 1000

        # We divide by 1000 because the library will clip audio that is 100 units away
        # so we convert from meters to kilometers so that we have more range
        distance = np.linalg.norm(self.location - self.l.location) / 1000
        if distance != 0: self.mul = min(self.mult/distance, self.max_mult)

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, velocity):
        """
        Sets the velocity of the audio source in m / s
        """
        self._velocity = np.array(velocity, dtype=np.float32)

    def move(self, dt):
        """
        Calculates the change in position of the audio source, as well as
        the change in pitch
        """

        # We divide by 1000 because the library will clip audio that is 100 units away
        # so we convert from meters to kilometers so that we have more range
        self.location += self.velocity * dt

        # Projection of relative velocity onto the distance vector
        dp = (self.location - self.l.location) / 1000
        dv = (self.l.velocity - self.velocity) / 1000
        dp_norm = dp / np.linalg.norm(dp)
        rv = np.inner(dv, dp_norm)

        # Update the rate at which the audio is played
        rate = sps / (sps - rv)
        if rate < 0: rate = max_rate
        rate = max(rate, min_rate)
        self.n.rate = rate

    @property
    def buffer(self, buffer):
        self.n.buffer = buffer

    def get_delta_time(self):
        dp = np.linalg.norm(self.location - self.l.location) / 1000
        dt = dp / sps

        return dt

    def play(self):
        if (self.use_delay):
            add_delay_event(self.get_delta_time(), self._play, ())
        else:
            self._play()

    def _play(self):
        """
        Starts playing audio
        """
        self.n.state = libaudioverse.NodeStates.playing

    def pause(self):
        if (self.use_delay):
            add_delay_event(self.get_delta_time(), self._pause, ())
        else:
            self._play()

    def _pause(self):
        """
        Pauses the audio to be continued later
        """
        self.n.state = libaudioverse.NodeStates.paused

    def reset(self):
        if (self.use_delay):
            add_delay_event(self.get_delta_time(), self._reset, ())
        else:
            self._play()

    def _reset(self):
        """
        Sets the play head to the beginning of the clip
        """
        self.n.reset()

    def set_audio_position(self, value):
        if (self.use_delay):
            add_delay_event(self.get_delta_time(), self._set_audio_position, ())
        else:
            self._play()

    def _set_audio_position(self, value):
        """
        Sets how far into the audio clip we are playing in seconds
        """
        self.n.position = value

if __name__ == '__main__':
    init()

    a = AudioListener()
    a.reverb.density = 0.9
    a.reverb.t60 = 0.2
    b = AudioBuffer('whoo.wav')
    S = AudioSource(a, b)
    S.location = [25, 1000, 0]

    print("Started playing")
    S.play()

    start_time = time.time()
    S.velocity = [-20, 0, 0]

    last_time = start_time
    while 1:
        curr_time = time.time()
        dt = curr_time - last_time
        S.move(dt)

        last_time = curr_time

        if curr_time - start_time > 4.5:
            break

    close()
