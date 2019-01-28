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
# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# Native
import os
import multiprocessing as mp
import json

# Third Party
import pystray
from pystray import MenuItem as item
from PIL import Image

# local
from bitalino_process import _process
            

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


def main():

    global state_list
    global specific_event_list
    global general_event
    global specific_event
    global icon
 
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
    image = Image.open("bitalino_logo_8rB_icon.ico")
    icon = pystray.Icon("name", image)
    icon_menu = [item('{}'.format(macAddr), set_state(i), checked=get_state(i))
                 for i, macAddr in enumerate(macAddress_list)]
    icon_menu = icon_menu + [item("Stop Acquisition", stop)]
    icon.menu = icon_menu

    icon.run()
    icon.stop()

if __name__ == '__main__':    
    mp.freeze_support()
    main()
    






    