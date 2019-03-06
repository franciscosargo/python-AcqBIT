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
    digitalOutput = np.array(list(ndsignal[-1, 1:3]) + digitalArray,
                             copy=False)
    device.trigger(digitalArray=digitalArray)
    return digitalOutput


def __find_bitalino(macAddress, deviceName, general_event, specific_event):
    """Loop to find and connect to the bitalino device by macAddress."""

    # Connection Loop
    print ('Looking for bitalino...'
           '-- NAME: {} -- ADDR: {}').format(deviceName, macAddress)

    while True:

        try:
            # Check for event interruption
            if (specific_event.is_set() or general_event.is_set()):
                raise ValueError('Closing the acquisition.')

            device = bt.BITalino(macAddress, timeout=1)  # connect to BITalino
            print ('Running!'
                   '-- NAME: {} -- ADDR: {}').format(deviceName, macAddress)

            break

        except ValueError as e:
            print ('{}'
                   '-- NAME: {} -- ADDR: {}').format(e, deviceName, macAddress)
            return None

        except Exception as e:
            print ('{}'
                   '-- NAME: {} -- ADDR: {}').format(e, deviceName, macAddress)
            pass

    return device


def __read_bitalino(device, path_to_save, macAddress, deviceName, setup,
                    acqChannels, acqLabels, digitalOutput,
                    samplingRate, nSamples, sync_delta, i_datetime,
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
        ioos.overwrite_dsets(r_group, acqChannels)

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
                ndsignal = device.read(nSamples)

                if i == 0:
                    time_init_acq = epoch_time()
                    old_sync_time = timing()
                    time_init_acq = (time_init_acq -
                                     np.true_divide(nSamples,
                                                    samplingRate))

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
                        digitalOutput = __sync_bitalino(device, ndsignal)
                        sync_time_flag = timing()
                        ioos.write_sync_time(r_group, digitalOutput,
                                             sync_time_flag)
                        old_sync_time = sync_time_flag

                # Compute necessary support for OpenSignals compatibility
                # if support:
                #   support = sp.compute_support(ndsignal)
                #  ioos.write_sp_h5file(r_group, acqChannels, support)

                # Check used system resources
                if mem_profile:
                    process = psutil.Process(os.getpid())

                    # Get memory in bytes
                    mem = process.memory_info().rss
                    profile_list[0] = mem

                # Send recieved data to websocket
                if interface:
                    #t_str = ndsignal[:100,:].tostring()
                    #t_str = '\n'.join(' '.join('%0.1f' %x for x in y) for y in ndsignal)
                    t_str = ndsignal.tobytes()
                    MESSAGE = t_str
                    s.sendto(MESSAGE, (UDP_IP, UDP_PORT))

                # Save time quantifiaction on file
                if time_profile or mem_profile:
                    with open(prof_file_path, 'a') as w:
                        for profile_item in profile_list:
                            print >> w, profile_item
                        print >> w, '\n'

                # Write data to h5 file
                ioos.write_h5file(r_group, acqChannels, ndsignal)

            except Exception as e:
                print ('{}'
                       '-- NAME: {} -- ADDR: {}').format(e, deviceName,
                                                         macAddress)
                break

    finally:

        if support:
            ioos.write_sp_h5file(r_group, support, acqChannels)

        f.close()

        if interface:
            s.close()
        e = 'The acquistion is succesfully closed.'
        print '{} -- NAME: {} -- ADDR: {}'.format(e, deviceName, macAddress)


def _process(path_to_save, macAddress, setup, general_event, specific_event):
    """Main logic for the acquisition loop."""

    # Parse configuration
    deviceName = setup.get('deviceName', 'Anonymous device')
    acqLabels = setup.get('acqLabels', ["A1", "A2", "A3", "A4", "A5", "A6"])
    acqChannels = setup.get('acqChannels', [0, 1, 2, 3, 4, 5])
    # resolution = setup.get('resolution', [ 4,  1,  1,  1,  1, 10,
    #                                      10, 10, 10, 6, 6])
    samplingRate = setup.get('samplingRate', 1000)
    master = setup.get('master', 0)
    syncInterval = setup.get('syncInterval') * 60
    digitalOutput = setup.get('digitalOutput', [1, 1])
    nSamples = setup.get('nSamples', 1000)
    master = setup.get('master', 0)
    support = setup.get('support', 0)
    time_profile = setup.get('time_profile', 1)
    mem_profile = setup.get('mem_profile', 1)
    interface = setup.get('interface', 1)
    port = setup.get('port', 8090)

    print port

    # Add subfolder for Device
    path_to_save = os.path.join(path_to_save, deviceName)
    if not os.path.exists(path_to_save):
        os.makedirs(path_to_save)

    # Enter Main loop, handling long-term acquisition
    # (restart the reading in the event of a disruption)
    while True:

        device = __find_bitalino(macAddress, deviceName,
                                 general_event, specific_event)

        # Check for event interruption
        if (specific_event.is_set() or general_event.is_set()):
            break

        # Start Acquisition
        device.start(samplingRate, acqChannels)
        device.socket.settimeout(5)

        # Get initial time of acquisition
        i_datetime_acq = datetime.datetime.now()
        i_datetime = i_datetime_acq

        # Read from device
        __read_bitalino(device, path_to_save, macAddress, deviceName, setup,
                        acqChannels, acqLabels, digitalOutput,
                        samplingRate, nSamples, syncInterval, i_datetime,
                        specific_event, general_event,
                        mem_profile, time_profile,
                        master, support, interface, port)

        device.close()  # close device

        # Check for event interuption
        if (specific_event.is_set() or general_event.is_set()):
            break
