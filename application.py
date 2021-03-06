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
from __future__ import print_function

import datetime
import json
import logging
import multiprocessing as mp
import os
import sys

import pystray
from PIL import Image
from pystray import MenuItem as item

import acqBIT.bitalino_process as bp

_process = bp._process
logger = logging.getLogger(__name__)

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
    conf_path = os.path.join(os.getcwd(), 'config.json')
    with open(conf_path) as json_data_file:
        mdata = json.load(json_data_file)
        print(mdata)

    # Create folder for the acquisition
    activity_name = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    print(activity_name)
    path_name = os.path.join('~', 'Desktop', 
                             'acqBIT', mdata['user'], activity_name)   
    path_to_save = os.path.expanduser(path_name)
    if not os.path.exists(path_to_save):
        os.makedirs(path_to_save)

    # Start acquisition
    devices = mdata['devices']
    specific_event_list = []
    process_list = []
    state_list = []
    macAddress_list = devices.keys()
    general_event = mp.Event()  # start general event

    # loop each device and start process
    for macAddr in macAddress_list:

        # launch acquisition process
        specific_event = mp.Event()
        p = mp.Process(target=_process, args=(path_to_save, macAddr, 
                                              devices[macAddr], 
                                              specific_event, general_event))
        p.start()

        # add to list of running processes
        specific_event_list.append(specific_event)
        process_list.append(p)
        state_list.append(1)

    # Create Icon
    # create menu
    icon_menu = []
    for i, macAddr in enumerate(macAddress_list):
        setup = devices[macAddr]
        device_name = setup['device_name']
        item_obj = item('{}'.format(device_name), set_state(i),
                        checked=get_state(i))
        icon_menu.append(item_obj)
    icon_menu = icon_menu + [item("Stop Acquisition", stop)]

    # set image
    img_path = os.path.join(os.getcwd(), 
                            'BITALINO-logo.png')
    image = Image.open(img_path)
    
    # run icon
    icon = pystray.Icon("name", image, menu=icon_menu)
    icon.run()
    icon.stop()

if __name__ == '__main__':
    mp.freeze_support()
    main()    
