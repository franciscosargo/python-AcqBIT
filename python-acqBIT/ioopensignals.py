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
# python
import os

# 3rd party
import h5py as h5
import numpy as np
import matplotlib.pyplot as plt


def open_h5file_os(path_file):
    """Wrap h5py constructor"""

    return h5.File(path_file)


def setup_h5file_os(path_file, macAddress):
    """Setup h5 file used to save the whole acquisition data, by copying existent template."""

    dummy_path_file = os.path.join(os.getcwd(), '../add_ons', 'opensignals_201607181669_2019-01-30_17-29-39.h5')
    ## Copy the contents from the dummy file
    with h5.File(dummy_path_file, 'r+') as dummy_f, h5.File(path_file, 'w') as f:
        r_group = dummy_f[dummy_f.keys()[0]]
        group_id = f.require_group('/')
        dummy_f.copy(r_group, group_id)
        old_group_name = f.keys()[0]
        f[str(macAddress)] = f[old_group_name]
        del f[old_group_name]

        print f.keys()
        

def _write_acq_channel(r_group, channelName, signal):
    """Write 1D signal from acquistion to the end of h5 dataset."""

    # Write acquisition channel to h5 dset
    nSamples = signal.shape[0]
    dset = r_group[channelName]
    nSamples_ds = dset.shape[0]
    dset.resize((nSamples_ds + nSamples, 1))
    dset[-nSamples:, 0] = signal


def write_h5file(r_group, acqChannels, ndsignal):
    """ Open and *acquisition data* write to a previously opened h5 file for the acquisition."""

    # Set names of the datasets, order according to the data array
    nseq_dset_names = ['raw/nSeq']
    digital_dset_names = ['digital/digital_{}'.format(dgNr + 1) for dgNr in xrange(0, 4)]
    analog_dset_names = ['raw/channel_{}'.format(chNr + 1) for chNr in acqChannels]
    dset_names = nseq_dset_names + digital_dset_names + analog_dset_names

    # Set the datasets on the file
    for i, dset_name in enumerate(dset_names):
        _write_acq_channel(r_group, dset_name, ndsignal[:, i])


def write_sp_h5file(r_group, acqChannels, support):
    """ Open and *support data* write to a previously opened h5 file for the acquisition."""
    digital_support_dset_names = ['dig_channel_{}'.format(dgNr + 1) for dgNr in xrange(0, 3)]
    analog_support_dset_names = ['channel_{}'.format(chNr + 1)  for chNr in acqChannels]
    #support_dset_names = ['support/level_{}/{}/{}'.format(level, dset_name, metric) 
                           #for dset_name in digital_support_dset_names + analog_support_dset_names
                           #for level in [10, 100, 1000]
                           #for metric in ['Mx', 'mx', 'mean', 'mean_x2', 'sd', 't']]
    
    # Set the datasets on the file
    for l, level in enumerate([10, 100, 1000]):
        for m, metric in  enumerate(['Mx', 'mx', 'mean', 'mean_x2', 'sd']):
            for i, dset_name in enumerate(digital_support_dset_names + analog_support_dset_names):
                dset_name = 'support/level_{}/{}/{}'.format(level, dset_name, metric) 
                support_arr = support[l][:, m, i]
                _write_acq_channel(r_group, dset_name, support_arr)


def write_sync_time(r_group, digitalOutput, sync_time_flag):
    """ Write synchronization event to disk, in the form of the subsequent digital output 
        and the respective time flag."""
        
    # Write digital array
    dset = r_group['events/digital']
    shape_0 = dset.shape[0]
    dset.resize((shape_0 + 1, 4))
    dset[shape_0, :] = digitalOutput

    # Write synchronization time flag
    dset = r_group['events/sync']
    shape_0 = dset.shape[0]
    dset.resize((shape_0 + 1, 1))
    dset[shape_0] = sync_time_flag


def write_t_support(r_group, acqChannels):
    digital_support_dset_names = ['dig_channel_{}'.format(dgNr + 1) for dgNr in xrange(0, 3)]
    analog_support_dset_names = ['channel_{}'.format(chNr + 1)  for chNr in acqChannels]
    #support_dset_names = ['support/level_{}/{}/{}'.format(level, dset_name, metric) 
                           #for dset_name in digital_support_dset_names + analog_support_dset_names
                           #for level in [10, 100, 1000]
                           #for metric in ['Mx', 'mx', 'mean', 'mean_x2', 'sd', 't']]
    
    # Set the datasets on the file
    for l, level in enumerate([10, 100, 1000]):
        for i, dset_name in enumerate(digital_support_dset_names + analog_support_dset_names):
            dset_name_Mx = 'support/level_{}/{}/Mx'.format(level, dset_name)
            dset_name = 'support/level_{}/{}/t'.format(level, dset_name)
            end = r_group[dset_name_Mx].shape[0]
            t = range(0, end, level)
            del r_group[dset_name]
            r_group[dset_name] = t


def overwrite_dsets(r_group, acqChannels):
    """ Overwrite existing template and corresponding datasets."""

    # Set names of the datasets, order according to the data array
    nseq_dset_names = ['raw/nSeq']
    digital_dset_names = ['digital/digital_{}'.format(dgNr + 1) for dgNr in xrange(0, 4)]
    analog_dset_names = ['raw/channel_{}'.format(chNr + 1)  for chNr in xrange(0, 6)]
    dset_names = nseq_dset_names + digital_dset_names + analog_dset_names
    digital_support_dset_names = ['dig_channel_{}'.format(dgNr) for dgNr in xrange(1, 4)]
    analog_support_dset_names = ['channel_{}'.format(chNr + 1)  for chNr in acqChannels]
    support_dset_names = ['support/level_{}/{}/{}'.format(level, dset_name, metric) 
                           for dset_name in digital_support_dset_names + analog_support_dset_names
                           for level in [10, 100, 1000]
                           for metric in ['Mx', 'mx', 'mean', 'mean_x2', 'sd']]

    # Set the datasets on the file
    for dset_name in dset_names:
        attrs = r_group[dset_name].attrs
        del r_group[dset_name]
        r_group.create_dataset(dset_name, 
                               dtype='uint16', shape=(0, 1), 
                               maxshape=(None, 1), chunks=(1024, 1))

        for k in attrs.keys():
            # Set attributes of the new dataset
            r_group[dset_name].attrs[k] = attrs[k]

    for dset_name in support_dset_names:
        del r_group[dset_name]
        r_group.create_dataset(dset_name, 
                               dtype='uint16', shape=(0, 1), 
                               maxshape=(None, 1), chunks=(1024, 1))

    dset_name = 'events/digital'
    del r_group[dset_name]
    r_group.create_dataset(dset_name, 
                           dtype='uint16', shape=(0, 4), 
                           maxshape=(None, 4), chunks=(1024, 1)) 

    dset_name = 'events/sync'
    del r_group[dset_name]
    r_group.create_dataset(dset_name, 
                           dtype='float32', shape=(0, 1), 
                           maxshape=(None, 1), chunks=(1024, 1))   

    
def get_analog_channel(r_group, acqChannel):
    dset_name = 'raw/channel_{}'.format(acqChannel)
    return r_group[dset_name][:]   


def get_root_group(file_obj):
    """Wrap extraction of root group from HDF5 file object"""

    return file_obj[file_obj.keys()[0]]





          










