# Python
import datetime
import os

# Third Party
import numpy as np
import bitalino as bt

# Local
import int_out as io


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
                    nSamples, master_flag,
                    sync_datetime, i_datetime, 
                    specific_event, general_event):
        """
		Loop to continuously read the channels from a connected bitalino device according to input configuration.
	    """

        # Acquisition Loop
        with io.open_h5file(path_to_save,  macAddress, acqChannels, acqLabels, nSamples) as f:

            # Acquisition iteration
            b_datetime = i_datetime
            for i in xrange(0, 2*60*60):

                try:
                    dataAcquired = device.read(nSamples)
                    io.write_h5file(f, macAddress, dataAcquired, acqChannels, nSamples)

                    # Check for synchronization
                    datetime_now = datetime.datetime.now()

                    ## Check for event interuption
                    if (specific_event.is_set() or general_event.is_set()):
                        raise ValueError('Closing the acquisition.')
                    
                    if setup['master']:
                        if  datetime_now - b_datetime >= sync_datetime:
                            print 'Syncing from master -- NAME: {} -- ADDR: {}'.format(deviceName, macAddress)
                            # Change digital output in master device
                            digitalOutput = [dataAcquired[-1, 3], dataAcquired[-1, 4]]
                            digitalArray = [int(not bool(dg_val))
                                            for dg_val in digitalOutput]
                            device.trigger(digitalArray=digitalArray)
                            digitalOutput = digitalArray
                            b_datetime = datetime_now

                            ## Save sync_time on hdf file (TO DO: should it be time_now?)
                            io.write_sync_datetime(f, datetime_now)


                except Exception as e:
                    io.create_opensignals_mdata(f, setup, i_datetime, i)
                    print '{} -- NAME: {} -- ADDR: {}'.format(e, deviceName, macAddress)
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

    ## Add subfolder for Device
    path_to_save = os.path.join(path_to_save, deviceName)
    if not os.path.exists(path_to_save):
        os.makedirs(path_to_save)

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
        __read_bitalino(device, path_to_save, macAddress, deviceName,
                        setup, acqChannels, acqLabels, digitalOutput, 
                        nSamples, master_flag,
                        sync_datetime, i_datetime, 
                        specific_event, general_event)

        device.close()  ## close device

        ## Check for event interuption
        if (specific_event.is_set() or general_event.is_set()):
            break  
