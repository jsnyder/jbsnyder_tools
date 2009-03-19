#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
accmouse.py translates accelerometer data from Firmata on Arduino into
mouse movements.


Copyright (c) 2009 James Snyder

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the \"Software\"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.


Computer Setup:
movemouse program is required to actually move mouse position

Arduino Setup:
Arduino has StandardFirmata firmware installed
Accelerometer is LIS2L02AS4, with X and Y output pins connected 
to Analog 0 & 1 on the Arduino
Both X and Y pins have a 4.75uF capacitor connected to ground (low pass
filtering)
"""

import time
import pyduino
from multiprocessing import Process, Queue
from ringbuffer import *
from subprocess import call


def adc_get_sample(arduino, pin):
    """ Iterate on processing data and return a data sample """

    arduino.iterate()
    return arduino.analog[pin].read()


def range_check(var, minval, maxval):
    """ Return var with range clipped at minval and maxval """

    if var < minval:
        var = minval
    if var > maxval:
        var = maxval
    return var


def get_analog_data(xqueue, yqueue):
    """ Get data from Arduino and put in queues """

    a = pyduino.Arduino('/dev/tty.usbserial-A6006kiD')

    a.analog[0].set_active(1)
    a.analog[1].set_active(1)

    (curx, cury) = (-1, -1)

    while not (xqueue.full() or yqueue.full()):

        while (curx, cury) == (-1, -1):
            curx = adc_get_sample(a, 0)
            cury = adc_get_sample(a, 1)

        (lastx, lasty) = (curx, cury)

        curx = 200 * (adc_get_sample(a, 0) - 0.479) + lastx
        cury = -200 * (adc_get_sample(a, 1) - 0.512) + lasty

        curx = range_check(curx, 0, 1280)
        cury = range_check(cury, 0, 800)

        xqueue.put(curx)
        yqueue.put(cury)


def update_cursor_position(*args):
    """ Pull all new values from queues and update cursor position """

    while not (xqueue.empty() or yqueue.empty()):
        DATABUF.append(xqueue.get())
        DATABUF2.append(yqueue.get())

    call(['./movemouse', str(DATABUF[-1]), str(DATABUF2[-1])])


if __name__ == '__main__':

    BUFSIZE = 10
    DATABUF = RingBuffer(BUFSIZE)
    DATABUF2 = RingBuffer(BUFSIZE)
    DATABUF.append(0)
    DATABUF2.append(0)

    (xqueue, yqueue) = (Queue(), Queue())
    proc = Process(target=get_analog_data, args=(xqueue, yqueue))
    proc.start()

    while 1:
        update_cursor_position()
        time.sleep(1.0 / 30.0)

    proc.join()
