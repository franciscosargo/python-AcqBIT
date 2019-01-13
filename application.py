"""
 * \author     Francisco Sargo
 * \version    1.0
 * \date       January 2019
 * 
 * \section LICENSE
 
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Lesser General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Lesser General Public License for more details.
 
 You should have received a copy of the GNU Lesser General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
 
"""

# Python
import time
import os
import multiprocessing 
import json

# Third Party
import bitalino as bt
import h5py as h5
import pystray
from pystray import MenuItem as item
from PIL import Image


if 0:
     import UserList
     import UserString
     import UserDict
     import itertools
     import collections
     import future.backports.misc
     import commands
     import base64
     import __buildin__
     import math
     import reprlib
     import functools
     import re
     import subprocess

def open_h5file(macAddress, nSamples, path_to_save):
    """ 
    Utility function to open and setup a maximum 2 hours duration h5 file for the acquisition
    """

    # Open file
    filename = time.strftime("test_%Y-%m-%d_%H-%M-%S", time.gmtime()) + '.h5'
    file_path = os.path.join(path_to_save, filename)

    # Open file
    f = h5.File(file_path, 'w')

    # Create the datasets according to OpenSignals standard
    root_group_name = macAddress + '/'
    r_grp = f.create_group(root_group_name)

    # Digital
    r_grp.create_dataset('digital/digital_1', dtype='uint16', shape=(nSamples, 1), maxshape=(2*60*60*nSamples, 1), chunks=(1024, 1))
    r_grp.create_dataset('digital/digital_2', dtype='uint16', shape=(nSamples, 1), maxshape=(2*60*60*nSamples, 1), chunks=(1024, 1))
    r_grp.create_dataset('digital/digital_3', dtype='uint16', shape=(nSamples, 1), maxshape=(2*60*60*nSamples, 1), chunks=(1024, 1))
    r_grp.create_dataset('digital/digital_4', dtype='uint16', shape=(nSamples, 1), maxshape=(2*60*60*nSamples, 1), chunks=(1024, 1))

    # Analog
    r_grp.create_dataset('raw/channel_1', dtype='uint16', shape=(nSamples, 1), maxshape=(2*60*60*nSamples, 1), chunks=(1024, 1))
    r_grp.create_dataset('raw/channel_2', dtype='uint16', shape=(nSamples, 1), maxshape=(2*60*60*nSamples, 1), chunks=(1024, 1))
    r_grp.create_dataset('raw/channel_3', dtype='uint16', shape=(nSamples, 1), maxshape=(2*60*60*nSamples, 1), chunks=(1024, 1))
    r_grp.create_dataset('raw/channel_4', dtype='uint16', shape=(nSamples, 1), maxshape=(2*60*60*nSamples, 1), chunks=(1024, 1))
    r_grp.create_dataset('raw/channel_5', dtype='uint16', shape=(nSamples, 1),maxshape=(2*60*60*nSamples, 1), chunks=(1024, 1))
    r_grp.create_dataset('raw/channel_6', dtype='uint16', shape=(nSamples, 1), maxshape=(2*60*60*nSamples, 1), chunks=(1024, 1))
    r_grp.create_dataset('raw/nSeq', dtype='uint16', shape=(nSamples, 1),  maxshape=(2*60*60*nSamples, 1), chunks=(1024, 1))

    # Events
    #r_grp.create_dataset('events/digital', dtype='uint32', shape= maxshape=(2*60*60*nSamples, 4), chunks=(512, 4))
    #r_grp.create_dataset('raw/sync', dtype='uint32', maxshape=(2*60*60*nSamples, 4), chunks=(512, 4))

    return f

def write_h5file(macAddress, file_object, signal):
    """ 
    Utility function to open and write to a previously opened h5 file for the acquisition
    """

    # Create the datasets according to OpenSignals standard
    root_group_name = macAddress + '/'
    r_grp = file_object[root_group_name]

    # Extract channels information
    digital_1 = signal[:, 0]
    digital_2 = signal[:, 1]
    digital_3 = signal[:, 2]
    digital_4 = signal[:, 4]


    # 

    # 



def _process(macAddress, setup):
    """
		Main logic for the acquisition loop.
	"""

    # Create directory
    path_name = os.path.join('~', 'Desktop', 'test', macAddress.replace(':', '-'))   
    user = os.path.expanduser(path_name)
    path_to_save = os.path.expanduser(path_name)

    if not os.path.exists(path_to_save):
        os.makedirs(path_to_save)
    
    # Set Characteristics of the acquisition
    batteryThreshold = setup['batteryThreshold']
    acqChannels = setup['acqChannels']
    samplingRate = setup['samplingRate']
    nSamples = setup['nSamples']
    digitalOutput = setup['digitalOutput']
    nChannels = len(digitalOutput) + len(acqChannels)
    
    while True:
        ## Connection Loop
        while True:
            try:
                device = bt.BITalino(macAddress)  # connect to BITalino
                print device.version()
                break
            except Exception as e:
                print e
                pass
                
        # Start Acquisition
        device.start(samplingRate, acqChannels)
        device.socket.settimeout(5)

        # Acquisition Loop
        with open_h5file(macAddress, nSamples, path_to_save) as f:
             # create dataset with maximum size of 2 hours

            for i in xrange(0, 2*60*60):
                try:
                    signal = device.read(nSamples) 
                    dataset.resize(((i+1)*nSamples, nChannels + 1))
                    dataset[i*nSamples:(i+1)*nSamples, :] = signal
    
                except Exception as e:
                    print e
                    break
        
        device.close()

def start_process(macAddress, setup):
    """ 
    Utility function to start acquisition from each device in a single process
    """

    # Start process
    p = multiprocessing.Process(target=_process, args=(macAddress, setup))
    p.start()

    return p

def stop():
    """ 
    Stops entire acquisition upon system tray menu interaction
    """
    for p in process_list:
        p.terminate()
    icon.stop()


if __name__ == '__main__':
 
    # Open Configuration file
    with open('config.json') as json_data_file:
        data = json.load(json_data_file)
        print(data)
    
    # Start acquisition
    devices = data['devices']
    process_list = []
    for d in devices.keys():
        # Start process
        p = multiprocessing.Process(target=_process, args=(d, devices[d]))
        p.start()
        process_list.append(p)

    # Create Icon
    image = Image.open("BITALINO-logo.png")
    icon = pystray.Icon("name", image)
    icon_menu = [item(d, lambda func: process_list[i].terminate())
                 for i, d in enumerate(devices.keys())]
    icon_menu = icon_menu + [item("Stop Acquisition", stop)]
    icon.menu = icon_menu

    icon.run()
    icon.stop()
    

    






    