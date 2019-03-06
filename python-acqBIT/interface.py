# -*- coding: utf-8 -*-
"""
This example demonstrates many of the 2D plotting capabilities
in pyqtgraph. All of the plots may be panned/scaled by dragging with 
the left/right mouse buttons. Right click on any plot to show a context menu.
"""

import json
import os
import socket
from contextlib import contextmanager

import numpy as np
import pyqtgraph as pg
from PIL import Image
from pyqtgraph.Qt import QtCore, QtGui


### **** TEMP ****
with open(os.path.join(os.getcwd(), '..', 'config.json')) as json_data_file:
        mdata = json.load(json_data_file)
        print(mdata)

# Parse device specification from .json
devices = mdata['devices']
mac_address = devices.keys()[0]
setup = devices[mac_address]
device_name = setup['deviceName']

# Get Channels information
acq_channels = setup['acqChannels']
acq_labels = setup['acqLabels']

n_samples = setup['nSamples']

app = QtGui.QApplication([])

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

# Create Windows
win = QtGui.QMainWindow()
title = ''
title_win = 'AcqBIT: {} - {}'.format(mac_address, device_name)
win.setWindowTitle(title_win)
win.resize(1000, 600)

# Create Main Widget
mainbox = QtGui.QWidget()
win.setCentralWidget(mainbox)
mainbox.setLayout(QtGui.QVBoxLayout())

mainbox.setStyleSheet("background-color:white;")

# Create Graphics Widget (pyqtgraph)
canvas = pg.GraphicsLayoutWidget()
mainbox.layout().addWidget(canvas)
 
#image = Image.open(os.path.join( os.getcwd(), '..', 'add_ons', 'acqBIT.png'))
#np_img = np.asarray(image)
#
#image_item = pg.ImageItem(image=np_img)
#rect = QtCore.QRect(130, 140, 61, 16)
#image_item.setRect(rect)
#image_item.rotate(90 + 180)
#
#view_box_logo = pg.ViewBox(enableMouse=False)
#view_box_logo.addItem(image_item)
## configure view for images
#view_box_logo.setAspectLocked()
##view_box_logo.invertY()
#canvas.addItem(view_box_logo, row=0, col=0)


colors_channels = [(48, 38, 131), (0, 15, 227), (0, 137, 62), (149, 193, 30), (253, 196, 0), (234, 124, 79)]

colors_acq_channels = [colors_channels[acq_channel] for acq_channel in acq_channels]


data = np.random.rand(3*1000)
# Add Plots for each channel of acquistion
plot_list = []
curve_list = []
for i, (channel, channel_label, color_channel) in enumerate(zip(acq_channels, acq_labels, colors_acq_channels)):
    plot_item = pg.PlotItem(title=channel_label, enableMenu=True, backgroud='w')
    plot_item.showGrid(x=True, y=True)
    Fs = 8000
    f = 5
    sample = 8000
    x = np.arange(sample)
    y = np.sin(2 * np.pi * f * x / Fs)

    # Make pen to draw plots
    pen = pg.mkPen(color=color_channel, width=0.5)
    plot_data = pg.PlotDataItem(pen=pen)
    plot_item.addItem(plot_data)
    canvas.addItem(plot_item, row=i/2 + 1, col=i%2)

    plot_list.append(plot_item)
    curve_list.append(plot_data)

win.show()

ptr = 0

UDP_IP = "127.0.0.1"
UDP_PORT = 8090

# recieve data from socket
s = socket.socket(socket.AF_INET,  # Internet
                    socket.SOCK_DGRAM)  # UDP
print 'Object done'
s.bind((UDP_IP, UDP_PORT))


def refresh(data, data_socket, nSamples):

    for i in xrange(0, data_socket.shape[1]):
        data[:-nSamples, i] = data[nSamples:, i]
        data[-nSamples:, i] = data_socket[:, i]

    return data


def update():
        global curve_list, plot_list, data, ptr, UDP_IP, UDP_PORT, s, n_samples, acq_channels

        # Fetch string data from UDP port
        data, addr = s.recvfrom(150000) # buffer size is 1024 bytes
        a = np.frombuffer(data, dtype='uint32')
        print a.shape

        print a
        #for curve, plot in zip(curve_list, plot_list):
            #curve.setData(y=data[ptr%10:])
            #if ptr == 0:
                #plot.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted7
        #ptr += 17

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)

# Enable antialiasing for prettier plots
#def update():
#
    #print 'Updating'
    #global curve, ptr, p6, UDP_IP, UDP_PORT, data, dvA_plots, dvB_plots

    # recieve data from socket
    #sock = socket.socket(socket.AF_INET, # Internet
                     #socket.SOCK_DGRAM) # UDP
    #sock.bind((UDP_IP, UDP_PORT))
    #dat, addr = sock.recvfrom(15000) # buffer size is 1024 bytes

    # create numpy array
    #a = np.matrix(dat).reshape(100,22)

    

    # refresh arrays
    #data = refresh(data, a)
#    
    #for  i in range(0,6):
        #dvA_plots[i].setData(data[:,i])
#
    #for i in range(6,12):
        #dvB_plots[i-6].setData(data[:,i])
#    
    #dvA_plots[6].setData(data[:,12])
    #dvB_plots[6].setData(data[:,13])

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        app.exec_()
