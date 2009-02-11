#!/usr/bin/env python
# Copyright (c) 2009 James Snyder
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#
# PROGRAM DESCRIPTION
# Plots real-time data from analog inputs from Firmata on Arduino
#
# COMPUTER SETUP
# Required Libs:
#  matplotlib, wx, pyduino, multiprocessing (works with backport for 2.5), numpy
#
# ARDUINO SETUP:
# Arduino has StandardFirmata firmware installed
# Connect things to analog inputs and set numinputs to how many adc inputs you want

import matplotlib
matplotlib.use('WXAgg')
matplotlib.rcParams['toolbar'] = 'None'

import wx, sys, time, pyduino
import pylab as p
import numpy as npy
from multiprocessing import Process, Queue
from ringbuffer import *

def adc_get_sample(pin):
    a.iterate()
    return a.analog[pin].read()

def get_analog_data(q):
    while not q.full():
        for i in range(numinputs):
            q.put((i, adc_get_sample(i)))

def update_line(*args):
    while not q.empty():
        newdata = q.get()
        databufs[newdata[0]].append(newdata[1])

    if update_line.background is None:
        update_line.background = canvas.copy_from_bbox(ax.bbox)

    # restore the clean slate background
    canvas.restore_region(update_line.background)
    # update the data
    for i in range(numinputs):
        lines[i].set_ydata(databufs[i])

    # just draw the animated artist
    for line in lines:
        ax.draw_artist(line)

    # just redraw the axes rectangle
    canvas.blit(ax.bbox)
    
    wx.WakeUpIdle()

if __name__ == '__main__':
    # Canvas Setup
    ax = p.subplot(111)
    canvas = ax.figure.canvas
    p.grid() # to ensure proper background restore

    # Arduino Setup
    a = pyduino.Arduino('/dev/tty.usbserial-A6006kiD')

    # Data Storage Setup
    numinputs = 5
    x = npy.linspace(0,1,100)
    databufs = [RingBuffer(x.size) for i in range(numinputs)]
    
    for i in range(numinputs):
        a.analog[i].set_active(1)

    for i in range(x.size):
        for ch in range(numinputs):
            databufs[ch].append(adc_get_sample(ch))

    lines = [p.plot(x,databufs[i], animated=True, lw=2).pop() for i in range(numinputs)]

    p.axis([min(x), max(x), 0, 1])
    
    q = Queue()
    proc = Process(target=get_analog_data, args=(q,))
    proc.start()
    update_line.background = None
    wx.EVT_IDLE(wx.GetApp(), update_line)
    p.show()
    proc.join()