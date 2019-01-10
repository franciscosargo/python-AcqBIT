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
import pdb
import multiprocessing 
import json

# Third Party
from bitalino import BITalino
import biosppy
from biosppy import storage
import h5py as h5
from PIL import Image, ImageDraw
from pystray import MenuItem as item
import pystray
from PIL import Image

print 'Hello'
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
                device = BITalino(macAddress)  # connect to BITalino
                print device.version()
                break
            except Exception as e:
                print e
                pass
                
        # Start Acquisition
        device.start(samplingRate, acqChannels)
        device.socket.settimeout(5)

        # Open file for I/O
        filename = time.strftime("%a, %d %b %Y %H %M %S +0000", time.gmtime()) + '.h5'

        # Acquisition Loop
        with h5.File(os.path.join(path_to_save, filename)) as f:
            dataset = f.create_dataset('ds', shape=(nSamples, nChannels + 1),
                                        maxshape=(2*60*60*nSamples, nChannels + 1))  # create dataset with maximum size of 2 hours

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
    

    






    