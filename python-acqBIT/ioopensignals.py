""" Provide I/O operations to produce opensignals complacent HDF5 files, using h5py.

The following module encloses a number of different methods to open, write,
and close HDF5 files with incoming data from a robust acquisition instance of the
python-acqBIT Application, with the use of h5py API.

:mod:`ioopensignals` -- I/O operations to produce opensignals complacent HDF5 files.
===================================

.. module:: ioopensignals
   :platform: Unix, Windows, MacOS
   :synopsis: I/O operations to produce opensignals complacent files.
.. moduleauthor:: Francisco Sargo <francisco.simao.sargo@tecnico.ulisboa.pt>
"""
import os
import pdb
import time

import h5py as h5
import numpy as np

import support as sp



def open_h5file_os(path_file):
    """Wrap h5py constructor"""
    return h5.File(path_file)


def get_root_group(file_obj):
    """Wrap extraction of root group from HDF5 file object"""
    return file_obj[file_obj.keys()[0]]


def setup_h5file_os(path_file, macAddress):
    """Setup h5 file used to save the whole acquisition data, 
       by copying existent template."""

    dummy_path_file = os.path.join(os.getcwd(), '../add_ons', 
                                  'opensignals_201604120230_2019-02-03_13-53-11.h5')
    ## Copy the contents from the dummy file
    with h5.File(dummy_path_file, 'r+') as dummy_f, h5.File(path_file, 'w') as f:
        r_group = dummy_f[dummy_f.keys()[0]]
        group_id = f.require_group('/')
        dummy_f.copy(r_group, group_id)
        old_group_name = f.keys()[0]
        if str(macAddress) not in old_group_name:
            f[str(macAddress)] = f[old_group_name]
            del f[old_group_name]


def overwrite_dsets(r_group, acq_channels, acq_labels):
    """
    :param r_group: root group of previously opened file in HDF5
    :type r_group:  h5py object
    :param acq_channels: numbers of analog channels in acquistion
    :type acq_channels: list
    :param acq_labels: name of analog in acquisiton
    :type acq_labels:  list
    :returns: None

    Overwrite existing OpenSignals template file and corresponding datasets.

    .. note:: See module implemented in support.py for the actual
              computation functions.
              is a memory intensive design decision.

    """

    # Get number of the channels in acquisition (digital and analog)
    dig_channels = range(1, 5)
    alog_channels = acq_channels
    alog_labels = acq_labels

    # Delete all relevant datasets
    del r_group['digital']
    del r_group['raw']
    del r_group['support']
    del r_group['events']

    # Go through each digital channel, create corresponding dataset
    for dig_channel in dig_channels:
        dset_name = 'digital/digital_{}'.format(dig_channel)
        r_group.create_dataset(dset_name,
                               dtype='uint16', shape=(0, 1),
                               maxshape=(None, 1), chunks=(1024, 1))

    # Go through each analog channel, create corresponding dataset
    # (with correct labels)
    for alog_channel, alog_label in zip(alog_channels, alog_labels):
        dset_name = 'raw/channel_{}'.format(alog_channel)
        r_group.create_dataset(dset_name,
                               dtype='uint16', shape=(0, 1),
                               maxshape=(None, 1), chunks=(1024, 1))
        attrs = r_group[dset_name].attrs
        attrs['label'] = alog_label
        attrs['sensor'] = 'RAW'
        attrs['special'] = '{{}}'

    # Create nseq array
    dset_name = 'raw/nSeq'
    r_group.create_dataset(dset_name,
                               dtype='uint16', shape=(0, 1),
                               maxshape=(None, 1), chunks=(1024, 1))

    # Create datasets to register digital channel triggering
    dset_name = 'events/digital'
    r_group.create_dataset(dset_name,
                           dtype='uint16', shape=(0, 4), 
                           maxshape=(None, 4), chunks=(1024, 1)) 

    # Create datasets with time of triggering
    # (The purpose of triggering is synchronization between devices)
    dset_name = 'events/sync'
    r_group.create_dataset(dset_name,
                           dtype='float32', shape=(0, 1), 
                           maxshape=(None, 1), chunks=(1024, 1))   


def write_h5file(r_group, acq_channels, ndsignal):
    """ Open and *acquisition data* write to a previously opened h5 file for the acquisition."""

    # Set names of the datasets, order according to the data array
    nseq_dset_names = ['raw/nSeq']
    digital_dset_names = ['digital/digital_{}'.format(dgNr) for dgNr in xrange(1, 5)]
    analog_dset_names = ['raw/channel_{}'.format(chNr) for chNr in acq_channels]
    dset_names = nseq_dset_names + digital_dset_names + analog_dset_names

    # Set the datasets on the file
    for i, dset_name in enumerate(dset_names):
        _write_acq_channel(r_group, dset_name, ndsignal[:, i])


def _write_acq_channel(r_group, channelName, signal):
    """Write 1D signal from acquistion to the end of h5 dataset."""

    # Write acquisition channel to h5 dset
    nsamples = signal.shape[0]
    dset = r_group[channelName]
    nsamples_ds = dset.shape[0]
    dset.resize((nsamples_ds + nsamples, 1))
    dset[-nsamples:, 0] = signal


def write_sync_time(r_group, digital_output, sync_time_flag):
    """ Write synchronization event to disk, in the form of the subsequent
        digital output and the respective time flag."""

    # Write digital array
    dset = r_group['events/digital']
    shape_0 = dset.shape[0]
    dset.resize((shape_0 + 1, 4))
    dset[shape_0, :] = digital_output

    # Write synchronization time flag
    dset = r_group['events/sync']
    shape_0 = dset.shape[0]
    dset.resize((shape_0 + 1, 1))
    dset[shape_0] = sync_time_flag


def write_support_to_h5file(r_group):
    """
    :param r_group: root group of previously opened file in HDF5
    :type r_group:  h5py object
    :returns: None

    Compute and write to hdf5 file the statistical rolling support (maximum,
    mean, standard deviation, ...) for each channel in acquistion.

    This action is required to create files readable by the OpenSignals
    software.

    This is a memory intensive design. It may take a lot of memory, but it
    decreases the computation time within the main acquisition loop.  

    .. note:: See module implemented in support.py for the actual
              computation functions.
              is a memory intensive design decision.

    """

    # Get datasets names
    digital_dsets_names, alog_dsets_names = get_acq_dset_names(r_group)
    dsets_names = digital_dsets_names + alog_dsets_names

    # Load the signal into memory in a 2D numpy array
    ndsignal = np.array([r_group[dset_name][:] 
                         for dset_name in dsets_names]).T[0]

    # Make sure the signal has the right dimensions
    assert ndsignal.shape[1] == len(dsets_names)
    assert ndsignal.shape[0] == r_group[dset_name].shape[0]

    # Compute rolling support and save it
    support = sp.compute_support(ndsignal)
    _write_support_to_h5file(r_group, support, dsets_names)


def _write_support_to_h5file(r_group, support, dsets_names):

    # Loop through each level
    for l, level in enumerate([10, 100, 1000]):
        for i, dset_name in enumerate(dsets_names):

            channel = dset_name.split('_')[-1]

            # Get name for support group 
            if 'digital' in dset_name:
                support_group_name = 'support/level_{}/dig_channel_{}/'.format(level, channel)
            if 'raw' in dset_name:
                support_group_name = 'support/level_{}/channel_{}/'.format(level, channel)

            # Save each array into appropriate dataset
            support_arr = support[l][0][:, i:i+1]
            dset_name = support_group_name + 'Mx'
            r_group.create_dataset(dset_name, dtype='uint16',
                                    data=support_arr)  # maximum

            support_arr = support[l][1][:, i:i+1]
            dset_name = support_group_name + 'mx'
            r_group.create_dataset(dset_name, dtype='uint16',
                                   data=support_arr)  # minimum

            support_arr = support[l][2][:, i:i+1]
            dset_name = support_group_name + 'mean'
            r_group.create_dataset(dset_name, dtype='float32',
                                   data=support_arr)  # mean

            support_arr = support[l][3][:, i:i+1]
            dset_name = support_group_name + 'mean_x2'
            r_group.create_dataset(dset_name, dtype='uint32',
                                   data=support_arr)  # squared mean

            support_arr = support[l][4][:, i:i+1]
            dset_name = support_group_name + 'sd'
            r_group.create_dataset(dset_name, dtype='float32',
                                   data=support_arr)  # standard deviation

            support_arr = np.array(support[l][5], copy=False).reshape(len(support[l][5]), 1)
            dset_name = support_group_name + 't'
            r_group.create_dataset(dset_name, dtype='uint32',
                                   data=support_arr)  # last sample number


def get_acq_dset_names(r_group):
    """
    :param r_group: root group of previously opened file in HDF5
    :type r_group:  h5py object
    :returns: one list with digital datasets names, one list with analog
              dataset names

    Get acquisition dataset names from file.

    .. note:: See module implemented in support.py
    """

    # Get channels from acquisition from file
    dig_channels_names = r_group['digital'].keys()
    alog_channels_names = r_group['raw'].keys()[:-1]

    # Get datasets names
    dig_dsets_names = ['digital/' + channel_name 
                        for channel_name in dig_channels_names]
    alog_dsets_names = ['raw/' + channel_name 
                        for channel_name in alog_channels_names]

    return dig_dsets_names, alog_dsets_names
    

def close_file(r_group, macAddress, device_name, setup,
               acq_channels, acq_labels, digital_output,
               sampling_rate, nsamples, sync_delta, i_datetime,
               mem_profile, time_profile,
               master, support, interface, port,
               time_init_acq):
    
    nsamples = r_group['digital/digital_1'].shape[0]
    attrs = r_group.attrs
    attrs['channels'] = acq_channels
    attrs['nsamples'] = nsamples
    attrs['device_name'] = device_name
    attrs['sampling_rate'] = sampling_rate

    t = time_init_acq
    fs = t - int(t)
    time_str = time.strftime("%H:%M:%S.", 
                             time.localtime(t)) + str(round(fs, 3))[2:]
    attrs['time'] = time_str
