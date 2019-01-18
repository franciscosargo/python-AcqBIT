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
import multiprocessing 
import json

# Third Party
import numpy as np
import bitalino as bt
import pystray
from pystray import MenuItem as item
from PIL import Image

# Local
import int_out as io

def _process(path_to_save, macAddress, setup):
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

    sync_datetime = datetime.timedelta(minutes=syncInterval)
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

        # Get initial time of acquisition
        i_time_acq = datetime.datetime.now()
        i_time = i_time_acq

        # Acquisition Loop
        with io.open_h5file(path_to_save,  macAddress, acqChannels, acqLabels, nSamples) as f:

            # Acquisition iteration
            for i in xrange(0, 2*60*60):

                try:
                    dataAcquired = device.read(nSamples) 
                    io.write_h5file(f, macAddress, dataAcquired, acqChannels, i, nSamples)

                    # Check for synchronization
                    time_now = datetime.datetime.now()
                    
                    if  time_now - i_time >= sync_datetime and setup['master']:
                        
                        digitalArray = [int(not bool(dg_val))
                                        for dg_val in digitalOutput]
                        device.trigger(digitalArray=digitalArray)
                        digitalOutput = digitalArray

                        ## Save sync_time on hdf file
                        #io.write_sync_datetime(f, sync_datetime)


                except Exception as e:
                    io.create_opensignals_mdata(f, setup, i_time_acq, i)
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

    # Stop all current processes
    for p in process_list:
        p.terminate()
    icon.stop()

if __name__ == '__main__':
 
    # Open Configuration file
    with open('config.json') as json_data_file:
        mdata = json.load(json_data_file)
        print(mdata)

    # Create folder for the acquisition
    path_name = os.path.join('~', 'Desktop', 'acqBIT', mdata['user'])   
    path_to_save = os.path.expanduser(path_name)

    if not os.path.exists(path_to_save):
        os.makedirs(path_to_save)

    # Start acquisition
    devices = mdata['devices']
    process_list = []
    for d in devices.keys():
        # Start process
        p = multiprocessing.Process(target=_process, args=(path_to_save, d, devices[d]))
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
    

    






    