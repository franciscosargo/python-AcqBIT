# Python
import timeit
import datetime
import os
import psutil

# Third Party
import numpy as np
import bitalino as bt

# Local
import int_out as io
import support as sp


def __sync_bitalino(device, f, setup,
                    datetime_now,
                    dataAcquired):
    """
    Function to trigger the digital pins of the master device, for synchronization purposes.
    """

    # Change digital output in master device
    digitalOutput = [dataAcquired[-1, 3], dataAcquired[-1, 4]]
    digitalArray = [int(not bool(dg_val))
                    for dg_val in digitalOutput]
    device.trigger(digitalArray=digitalArray)
    digitalOutput = digitalArray

    ## Save sync_time on hdf file (TO DO: should it be time_now?)
    io.write_sync_datetime(f, datetime_now)


def __find_bitalino(macAddress, deviceName, general_event, specific_event):
        """
		Loop to find and connect to the bitalino device by macAddress.
	    """
        
        ## Connection Loop
        print 'Looking for bitalino... -- NAME: {} -- ADDR: {}'.format(deviceName, macAddress)
        while True:
                    
            try:
                ## Check for event interruption
                if (specific_event.is_set() or general_event.is_set()):
                    raise ValueError('Closing the acquisition.')

                device = bt.BITalino(macAddress, timeout=5)  # connect to BITalino
                print 'Running! -- NAME: {} -- ADDR: {}'.format(deviceName, macAddress)

                break

            except ValueError as e:
                print '{} -- NAME: {} -- ADDR: {}'.format(e, deviceName, macAddress)
                return None
            
            except Exception as e:
                #print '{} -- NAME: {} -- ADDR: {}'.format(e, deviceName, macAddress)
                pass

        return device


def __read_bitalino(device, path_to_save, macAddress, deviceName, setup,
                    acqChannels, acqLabels, digitalOutput, 
                    nSamples, sync_delta, i_datetime, 
                    specific_event, general_event,
                    mem_profile, time_profile,
                    master, support):
        """
		Loop to continuously read the channels from a connected bitalino device according to input configuration.
	    """

        # Acquisition Loop
        with io.open_h5file(path_to_save,  macAddress, acqChannels, acqLabels, nSamples) as f:
            
            # Acquisition iteration
            old_sync_datetime = i_datetime

            for i in xrange(0, 2*60*60):

                try:

                    ## Check for event interuption
                    if (specific_event.is_set() or general_event.is_set()):
                        raise ValueError('Closing the acquisition.')

                    ## Check for time profiling
                    if time_profile:
                        time_before_read = timeit.default_timer()
                        
                    dataAcquired = device.read(nSamples)

                    ## Check for time profiling
                    if time_profile:
                        time_after_read = timeit.default_timer()
                        #io.log_time(f, time_before_read, time_after_read)

                    ## Check for synchronization
                    if master:
                        datetime_now = datetime.datetime.now()
                        if  datetime_now - old_sync_datetime >= sync_delta:
                            __sync_bitalino(device, f, setup, datetime_now, dataAcquired)
                            old_sync_datetime = datetime_now

                    ## Compute necessary support for OpenSignals compatibility
                    print support
                    if support:
                        support = sp.compute_support(dataAcquired)
                        print support

                    ## Check used system resources
                    if mem_profile:
                        mem = psutil.virtual_memory()['used']
                        #io.log_mem(f, mem)

                    io.write_h5file(f, macAddress, dataAcquired, 
                                    acqChannels, nSamples)
                        

                except Exception as e:
                    #io.create_opensignals_mdata(f, setup, i_datetime, i)
                    print '{} -- NAME: {} -- ADDR: {}'.format(e, deviceName, macAddress)
                    break


def _process(path_to_save, macAddress, setup, general_event, specific_event):
    """
		Main logic for the acquisition loop.
	"""

    # Parse configuration
    deviceName = setup.get('deviceName', 'Anonymous device')
    acqLabels = setup.get('acqLabels', ["A1", "A2", "A3", "A4", "A5", "A6"])
    acqChannels = setup.get('acqChannels', [0, 1, 2, 3, 4, 5])
    resolution = setup.get('resolution', [ 4,  1,  1,  1,  1, 10, 10, 10, 10,  6,  6])
    samplingRate = setup.get('samplingRate', 1000)
    master = setup.get('master', 0)
    syncInterval = setup.get('syncInterval')
    digitalOutput = setup.get('digitalOutput', [1, 1])
    nSamples = setup.get('nSamples', 1000)
    master = setup.get('master', 0)
    support = setup.get('support', 0)
    time_profile = setup.get('time_profile', 0)
    mem_profile = setup.get('mem_profile', 0)

    # Allocate sychronization interval
    if master:
        sync_delta = datetime.timedelta(minutes=syncInterval)
        syncInterval = sync_delta

    ## Add subfolder for Device
    path_to_save = os.path.join(path_to_save, deviceName)
    if not os.path.exists(path_to_save):
        os.makedirs(path_to_save)

    # Enter Main loop, handling long-term acquisition (restart the samples reading in the event of a disruption)
    while True:

        device = __find_bitalino(macAddress, deviceName, general_event, specific_event)

        ## Check for event interruption
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
                        nSamples, syncInterval, i_datetime, 
                        specific_event, general_event,
                        mem_profile, time_profile,
                        master, support)

        device.close()  ## close device

        ## Check for event interuption
        if (specific_event.is_set() or general_event.is_set()):
            break  
