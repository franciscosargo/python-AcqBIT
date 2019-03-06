# Python
import time
import datetime
import os
import sys
import psutil
import socket

# Third Party
import bitalino as bt
import numpy as np

# Local
import ioopensignals as ioos


# Determine timing configuration (Platform dependent)
if sys.platform == 'win32':
    epoch_time = time.time
    timing = time.clock

if sys.platform == 'darwin' or sys.platform == 'linux2':
    epoch_time = time.time
    timing = time.time


def __sync_bitalino(device,
                    ndsignal):
    """Function to trigger the digital pins of the master device,
       negating current state,
       a mark which serves synchronization purposes."""

    # Change digital output in master device
    digitalArray = [int(not bool(dg_val))
                    for dg_val in list(ndsignal[-1, 3:5])]
    digital_output = np.array(list(ndsignal[-1, 1:3]) + digitalArray,
                             copy=False)
    device.trigger(digitalArray=digitalArray)
    return digital_output


def __find_bitalino(macAddress, device_name, general_event, specific_event):
    """Loop to find and connect to the bitalino device by macAddress."""

    # Connection Loop
    print ('Looking for bitalino...'
           '-- NAME: {} -- ADDR: {}').format(device_name, macAddress)

    while True:

        try:
            # Check for event interruption
            if (specific_event.is_set() or general_event.is_set()):
                raise ValueError('Closing the acquisition.')

            device = bt.BITalino(macAddress, timeout=1)  # connect to BITalino
            print ('Running!'
                   '-- NAME: {} -- ADDR: {}').format(device_name, macAddress)

            break

        except ValueError as e:
            print ('{}'
                   '-- NAME: {} -- ADDR: {}').format(e, device_name, macAddress)
            return None

        except Exception as e:
            print ('{}'
                   '-- NAME: {} -- ADDR: {}').format(e, device_name, macAddress)
            pass

    return device


def __read_bitalino(device, path_to_save, macAddress, device_name, setup,
                    acq_channels, acq_labels, digital_output,
                    sampling_rate, nsamples, sync_delta, i_datetime,
                    specific_event, general_event,
                    mem_profile, time_profile,
                    master, support, interface, port):
    """Loop to continuously read the channels from a connected bitalino
       device according to input configuration."""

    # Open file
    file_date = datetime.datetime.now().strftime("{}_%Y-%m-%d_%H-%M-%S")
    file_date = file_date.format(macAddress.replace(':', ''))
    filename = file_date + '.h5'
    prof_filename = file_date + '_profiling' + '.txt'
    file_path = os.path.join(path_to_save, filename)
    prof_file_path = os.path.join(path_to_save, prof_filename)

    ioos.setup_h5file_os(file_path, macAddress)

    # Acquisition Loop
    try:

        f = ioos.open_h5file_os(file_path)
        # Get base group from file
        r_group = ioos.get_root_group(f)
        ioos.overwrite_dsets(r_group, acq_channels)

        if interface:
            UDP_IP = "127.0.0.1"
            UDP_PORT = port
            s = socket.socket(socket.AF_INET,  # Internet
                              socket.SOCK_DGRAM)  # UDP

        for i in xrange(0, 2*60*60):

            try:

                # Check for event interuption
                if (specific_event.is_set() or general_event.is_set()):
                    raise ValueError('Closing the acquisition...')

                # Initiate profiling structure
                if time_profile or mem_profile:
                    profile_list = [0, 0, 0]

                # Check for time profiling
                if time_profile:
                    time_before_read = timing()
                    profile_list[1] = time_before_read

                # Read array of samples from the device in acquisition
                ndsignal = device.read(nsamples)

                if i == 0:
                    time_init_acq = epoch_time()
                    old_sync_time = timing()
                    time_init_acq = (time_init_acq -
                                     np.true_divide(nsamples,
                                                    sampling_rate))

                # Check for time profiling
                if time_profile:
                    # Allocate values to deal with timed operations
                    # during acquisiton
                    time_after_read = timing()
                    profile_list[2] = time_after_read

                # Check for synchronization
                if master:
                    time_now = timing()
                    if (time_now - old_sync_time) >= sync_delta:

                        # Synchronize the device, sync_time_flag
                        #  should have high precision
                        digital_output = __sync_bitalino(device, ndsignal)
                        sync_time_flag = timing()
                        ioos.write_sync_time(r_group, digital_output,
                                             sync_time_flag)
                        old_sync_time = sync_time_flag

                # Check used system resources
                if mem_profile:
                    process = psutil.Process(os.getpid())

                    # Get memory in bytes
                    mem = process.memory_info().rss
                    profile_list[0] = mem

                # Send recieved data to websocket
                if interface:
                    t_str = ndsignal.tobytes()
                    MESSAGE = t_str
                    s.sendto(MESSAGE, (UDP_IP, UDP_PORT))

                # Save time quantifiaction on file
                if time_profile or mem_profile:
                    with open(prof_file_path, 'a') as w:
                        #for profile_item in profile_list:
                            #print >> w, profile_item
                        print >> w, profile_list
                        print >> w, '\n'

                # Write data to h5 file
                ioos.write_h5file(r_group, acq_channels, ndsignal)

            except Exception as e:
                print ('{}'
                       '-- NAME: {} -- ADDR: {}').format(e, device_name,
                                                         macAddress)
                break

    finally:

        if support:
            ioos.write_sp_h5file(r_group, support, acq_channels)

        f.close()

        if interface:
            s.close()
        e = 'The acquistion is succesfully closed.'
        print '{} -- NAME: {} -- ADDR: {}'.format(e, device_name, macAddress)


def _process(path_to_save, macAddress, setup, general_event, specific_event):
    """Main logic for the acquisition loop."""

    # Parse configuration
    device_name = setup.get('device_name', 'Anonymous device')
    acq_labels = setup.get('acq_labels', ["A1", "A2", "A3", "A4", "A5", "A6"])
    acq_channels = setup.get('acq_channels', [0, 1, 2, 3, 4, 5])
    # resolution = setup.get('resolution', [ 4,  1,  1,  1,  1, 10,
    #                                      10, 10, 10, 6, 6])
    sampling_rate = setup.get('sampling_rate', 1000)
    master = setup.get('master', 0)
    sync_interval = setup.get('sync_interval') * 60
    digital_output = setup.get('digital_output', [1, 1])
    nsamples = setup.get('acq_nsamples', 1000)
    master = setup.get('master', 0)
    support = setup.get('support', 0)
    time_profile = setup.get('time_profile', 1)
    mem_profile = setup.get('mem_profile', 1)
    interface = setup.get('interface', 1)
    port = setup.get('port', 8090)

    # Add subfolder for Device
    path_to_save = os.path.join(path_to_save, device_name)
    if not os.path.exists(path_to_save):
        os.makedirs(path_to_save)

    # Enter Main loop, handling long-term acquisition
    # (restart the reading in the event of a disruption)
    while True:

        device = __find_bitalino(macAddress, device_name,
                                 general_event, specific_event)

        # Check for event interruption
        if (specific_event.is_set() or general_event.is_set()):
            break

        # Start Acquisition
        device.start(sampling_rate, [channel - 1 for channel in acq_channels])
        device.socket.settimeout(5)

        # Get initial time of acquisition
        i_datetime_acq = datetime.datetime.now()
        i_datetime = i_datetime_acq

        # Read from device
        __read_bitalino(device, path_to_save, macAddress, device_name, setup,
                        acq_channels, acq_labels, digital_output,
                        sampling_rate, nsamples, sync_interval, i_datetime,
                        specific_event, general_event,
                        mem_profile, time_profile,
                        master, support, interface, port)

        device.close()  # close device

        # Check for event interuption
        if (specific_event.is_set() or general_event.is_set()):
            break
