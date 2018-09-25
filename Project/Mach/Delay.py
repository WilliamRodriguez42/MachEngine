from threading import Thread
import time

class DelayEvent:
    """
    Often times, audio events need to be delayed.
    So this class holds all of the information necessary to call a callback function
    after a set amount of time has passed
    """
    def __init__(self, stop_time, callback, args):
        self.stop_time = stop_time
        self.callback = callback
        self.args = args

def add_delay_event(delta_time, callback, args):
    """
    Appends a new delay_event to the events list.
    delta_time is measured in seconds
    """
    start_time = time.time()
    stop_time = start_time + delta_time

    de = DelayEvent(stop_time, callback, args)
    events.append(de)

events = []
stop = False
accuracy = 0.01
def delay():
    """
    Repeatedly checks for events to be called
    """
    while not stop:
        curr_time = time.time()
        for i, e in enumerate(events):
            if e.stop_time <= curr_time:
                e.callback(*e.args)
                del events[i]

        time.sleep(accuracy)

delay_thread = None
def init():
    delay_thread = Thread(target = delay)
    delay_thread.daemon = True
    delay_thread.start()

def close():
    global stop
    stop = True
    time.sleep(accuracy * 2)

if __name__ == '__main__':
    def test(s):
        print(s)

    init()
    add_delay_event(2, test, ('hi',))
    time.sleep(4)
    close()
