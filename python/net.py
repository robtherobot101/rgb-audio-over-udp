from __future__ import print_function
from __future__ import division

import platform
import numpy as np
import config

import socket
import signal
import sys

UDP_IP = "192.168.0.3"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def signal_handler(signal, frame):
    # turn off
    sock.close()
    sys.exit()

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

_gamma = np.load(config.GAMMA_TABLE_PATH)
"""Gamma lookup table used for nonlinear brightness correction"""

_prev_pixels = np.tile(253, (3, config.N_PIXELS))
"""Pixel values that were most recently displayed on the LED strip"""

pixels = np.tile(1, (3, config.N_PIXELS))
"""Pixel values for the LED strip"""

_is_python_2 = int(platform.python_version_tuple()[0]) == 2


def _update_net():
    """Sends new LED values over socket"""
    global pixels, _prev_pixels
    # Truncate values and cast to integer
    pixels = np.clip(pixels, 0, 255).astype(np.uint32)
    # Optional gamma correction
    p = _gamma[pixels] if config.SOFTWARE_GAMMA_CORRECTION else np.copy(pixels)
    # Encode 24-bit LED values in 32 bit integers
    r = np.left_shift(p[0][:].astype(np.uint32), 8)
    g = np.left_shift(p[1][:].astype(np.uint32), 16)
    b = p[2][:].astype(np.uint32)
    rgb = np.bitwise_or(np.bitwise_or(r, g), b)
    sock.sendto(rgb.tobytes(), (UDP_IP, UDP_PORT))


def update():
    """Updates the LED strip values"""
    _update_net()


# Execute this file to run a LED strand test
# If everything is working, you should see a red, green, and blue pixel scroll
# across the LED strip continuously
if __name__ == '__main__':
    import time
    # Turn all pixels off
    pixels *= 0
    pixels[0, 0] = 255  # Set 1st pixel red
    pixels[1, 1] = 255  # Set 2nd pixel green
    pixels[2, 2] = 255  # Set 3rd pixel blue
    print('Starting LED strand test')
    while True:
        pixels = np.roll(pixels, 1, axis=1)
        update()
        time.sleep(.1)
