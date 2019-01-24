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

# Native
import datetime
import os
import multiprocessing as mp
import json

# Third Party
import numpy as np
import bitalino as bt
import pystray
from pystray import MenuItem as item
from PIL import Image

# Local
import int_out as io


def __find_bitalino(macAddress, general_event, specific_event):
        """
		Loop to find and connect to the bitalino device by macAddress.
	    """
        
        ## Connection Loop
        while True:
                    
            try:
                ## Check for event interruption
                if (specific_event.is_set() or general_event.is_set()):
                    raise ValueError('The device {} is closing.'.format(macAddress))

                device = bt.BITalino(macAddress, timeout=100)  # connect to BITalino
                print device.version()

                break

            except ValueError as e:
                print e
                return None
            
            except Exception as e:
                print '{} -- {}'.format(e, macAddress)
                pass

        return device


def __read_bitalino(device, path_to_save, macAddress, setup,
                    acqChannels, acqLabels, digitalOutput, 
                    nSamples, master_flag,
                    sync_datetime, i_datetime, 
                    specific_event, general_event):
        """
		Loop to continuously read the channels from a connected bitalino device according to input configuration.
	    """

        # Acquisition Loop
        with io.open_h5file(path_to_save,  macAddress, acqChannels, acqLabels, nSamples) as f:

            # Acquisition iteration
            for i in xrange(0, 2*60*60):

                try:
                    dataAcquired = device.read(nSamples) 
                    io.write_h5file(f, macAddress, dataAcquired, acqChannels, nSamples)

                    # Check for synchronization
                    datetime_now = datetime.datetime.now()

                    ## Check for event interuption
                    if (specific_event.is_set() or general_event.is_set()):
                        raise ValueError('The device {} is closing.'.format(macAddress))
                    
                    if  datetime_now - i_datetime >= sync_datetime and setup['master']:
                        
                        # Change digital output in master device
                        digitalArray = [int(not bool(dg_val))
                                        for dg_val in digitalOutput]
                        device.trigger(digitalArray=digitalArray)
                        digitalOutput = digitalArray

                        ## Save sync_time on hdf file (TO DO: should it be time_now?)
                        io.write_sync_datetime(f, datetime_now)

                except Exception as e:
                    io.create_opensignals_mdata(f, setup, i_datetime, i)
                    print '{} -- {}'.format(e, macAddress)
                    break


def _process(path_to_save, macAddress, setup, general_event, specific_event):
    """
		Main logic for the acquisition loop.
	"""

    # Set metadata for the acquisition
    batteryThreshold = setup['batteryThreshold']
    acqChannels = setup['acqChannels']
    acqLabels = setup['acqLabels']
    samplingRate = setup['samplingRate']
    nSamples = setup['nSamples']
    digitalOutput = setup['digitalOutput']
    syncInterval = setup['syncInterval']  # minutes
    deviceName = setup['deviceName']
    resolution = setup['resolution']
    master_flag = setup['master']

    sync_datetime = datetime.timedelta(minutes=syncInterval)
    nChannels = len(digitalOutput) + len(acqChannels)

    while True:

        device = __find_bitalino(macAddress, general_event, specific_event)

        ## Check for event interuption
        if (specific_event.is_set() or general_event.is_set()):
            break   
                
        # Start Acquisition
        device.start(samplingRate, acqChannels)
        device.socket.settimeout(5)

        # Get initial time of acquisition
        i_datetime_acq = datetime.datetime.now()
        i_datetime = i_datetime_acq

        # Read from device
        __read_bitalino(device, path_to_save, macAddress, setup,
                        acqChannels, acqLabels, digitalOutput, 
                        nSamples, master_flag,
                        sync_datetime, i_datetime, 
                        specific_event, general_event)

        device.close()  ## close device

        ## Check for event interuption
        if (specific_event.is_set() or general_event.is_set()):
            break  
            


# Icon methods
def set_state(v):
    def inner(icon, item):
        global state_list, specific_event_list
        state_list[v] = not state_list[v]
        specific_event_list[v].set()
    return inner
    

def get_state(v):
    def inner(item):
        global state_list
        return state_list[v]
    return inner


def stop():
    general_event.set()  # set stoping event
    icon.stop()  # kill icon


if __name__ == '__main__':

    global state_list
    global specific_event_list

    mp.freeze_support()
 
    # Open Configuration file
    with open('config.json') as json_data_file:
        mdata = json.load(json_data_file)
        print(mdata)

    # Create folder for the acquisition
    path_name = os.path.join('~', 'Desktop', 'acqBIT', mdata['user'])   
    path_to_save = os.path.expanduser(path_name)

    if not os.path.exists(path_to_save):
        os.makedirs(path_to_save)

    # Open General event for acquisition
    general_event = mp.Event()

    # Start acquisition
    devices = mdata['devices']
    specific_event_list = []
    process_list = []
    state_list = []
    macAddress_list = devices.keys()
    for macAddr in macAddress_list:
        # Start process
        specific_event = mp.Event()
        p = mp.Process(target=_process, args=(path_to_save, macAddr, devices[macAddr], 
                                              specific_event, general_event))
        p.start()
        specific_event_list.append(specific_event)
        process_list.append(p)
        state_list.append(1)

    # Create Icon
    image = Image.open("BITALINO-logo.png")
    icon = pystray.Icon("name", image)
    icon_menu = [item('{}'.format(macAddr), set_state(i), checked=get_state(i))
                 for i, macAddr in enumerate(macAddress_list)]
    icon_menu = icon_menu + [item("Stop Acquisition", stop)]
    icon.menu = icon_menu

    icon.run()
    icon.stop()

    






    