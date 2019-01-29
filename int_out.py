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

# python
import time
import datetime
import os

# 3rd party
import numpy as np
import h5py as h5


def _write_acq_channel(r_grp, channelName, channelSignal, nSamples):
    """
    Write 1D signal from acquistion to the end of h5 dataset
    """
    
    # Write acquisition channel to h5 dset
    dset = r_grp[channelName]
    dset.resize((dset.shape[0] + nSamples, 1))
    dset[-nSamples:, 0] = channelSignal


def write_h5file(file_object, macAddress, dataAcquired, acqChannels, nSamples):
    """ 
    Utility function to open and write to a previously opened h5 file for the acquisition
    """

    # Create the datasets according to OpenSignals standard
    root_group_name = macAddress + '/'
    r_grp = file_object[root_group_name]

    # Set names of the datasets, order according to the data array
    nseq_dset_names = ['raw/nseq']
    digital_dset_names = ['digital/digital_{}'.format(dgNr + 1) for dgNr in xrange(0, 4)]
    analog_dset_names = ['raw/channel_{}'.format(chNr + 1)  for chNr in acqChannels]
    dset_names = nseq_dset_names + digital_dset_names + analog_dset_names

    # Set the datasets on the file
    for i, dset_name in enumerate(dset_names):
        _write_acq_channel(r_grp, dset_name, dataAcquired[:, i], nSamples)


def open_h5file(path_to_save, macAddress, acqChannels, acqLabels, nSamples):
    """ 
    Utility function to open and setup a maximum 2 hours duration h5 file for the acquisition
    """

    # Open file
    filename = datetime.datetime.now().strftime("{}_%Y-%m-%d_%H-%M-%S".format(macAddress.replace(':', ''))) + '.h5'
    file_path = os.path.join(path_to_save, filename)

    # Copy file 
    f = h5.File(file_path, 'w')

    # Create the datasets according to OpenSignals standard
    root_group_name = macAddress + '/'
    r_grp = f.create_group(root_group_name)

    # Set names of the datasets, order according to the data array
    nseq_dset_names = ['raw/nseq']
    digital_dset_names = ['digital/digital_{}'.format(dgNr + 1) for dgNr in xrange(0, 4)]
    analog_dset_names = ['raw/channel_{}'.format(chNr + 1)  for chNr in acqChannels]
    dset_names = nseq_dset_names + digital_dset_names + analog_dset_names

    # Set the datasets on the file
    for dset_name in dset_names:
        r_grp.create_dataset(dset_name, 
                             dtype='uint16', shape=(0, 1), 
                             maxshape=(None, 1), chunks=(1024, 1))

    # Set event datasets on file
    root_group_name = macAddress + '/'
    r_grp = f[root_group_name]
    r_grp_events = r_grp.create_group('events/')
    r_grp_events.create_dataset('digital', dtype='uint32',
                          shape=(4, 4))
    r_grp_events.create_dataset('sync', dtype='uint32',
                          maxshape=(None, 6), chunks=(1024, 1), shape=(0, 6))

    return f


def create_opensignals_mdata(f, setup, initialTimeAcquisition, i):
    """ 
    Utility function to close h5 file for the acquisition
    """

    # Set attributes for the file
    i_time_acq = initialTimeAcquisition
    nsamples = i*setup['nSamples']  ## This is the final number of samples in the acquisition
    duration = '{}s'.format(nsamples/setup['samplingRate'])
    macAddress = setup['macAddress']

    attrs = {u'channels': setup['acqChannels'],
             u'comments': u'',
             u'date': i_time_acq.strftime("%Y-%m-%d"),
             u'device': u'bitalino_rev',
             u'device connection': 'BTH{}'.format(setup['macAddress']),
             u'device name': setup['deviceName'],
             u'digital IO': setup['digitalOutput'],
             u'duration': duration,
             u'firmware version': 1281,
             u'keywords': u'',
             u'macaddress': setup['macAddress'],
             u'mode': 0,
             u'nsamples': nsamples,
             u'resolution': setup['resolution'],
             u'sampling rate': setup['samplingRate'],
             u'sync interval': setup['syncInterval'],
             u'time': i_time_acq.now().strftime("%H:%M:%S")}

    ## Open signals backward compatibility **
    root_group_name = macAddress + '/'
    r_grp = f[root_group_name]
    r_grp.create_group('plugin/action')
    r_grp_events = r_grp.create_group('plugin/events/')
    r_grp_events.create_dataset('events_definition', dtype='uint32',
                                 shape=(0, 7))
    r_grp_events.create_dataset('events_on', dtype='uint32',
                                 shape=(0, 11))
    r_grp.create_group('plugin/signalStatistics')

    # Signal support datasets
    for level in [10, 100, 1000]:
        for name in ['Mx', 'mean', 'mean_x2', 'mx', 'sd', 't']:

            for chNr in setup['acqChannels']: 
                c = chNr + 1
                r_grp.create_dataset('support/level_{}/channel_{}/{}'.format(level, c, name), 
                                      dtype='uint16', shape=(nsamples/level, 1))

            for dgNr in xrange(0, 4):
                d = dgNr + 1
                r_grp.create_dataset('support/level_{}/dig_channel_{}/{}'.format(level, d, name),
                                      dtype='uint16', shape=(nsamples/level, 1))

    for k in attrs.keys():
        # Set attributes of the root group
        f[f.keys()[0]].attrs[k] = attrs[k]


def write_sync_datetime(f, datetime_now):
    """ 
    Utility function to append the datetime of the new device synchronization 
    event to the appropriate dataset in the acquisition file.
    """ 

    my_dt_ob = datetime_now
    # Convert datetime to list
    date_list = [my_dt_ob.year, my_dt_ob.month, my_dt_ob.day, my_dt_ob.hour, my_dt_ob.minute, my_dt_ob.second]
    r_grp = f[f.keys()[0]]
    dset = r_grp['events/sync']
    dset.resize((dset.shape[0] + 1, 6))
    dset[-1, 0:len(date_list)] = date_list





