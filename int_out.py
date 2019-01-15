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

def _write_acq_channel(r_grp, channelName, channelSignal, i, nSamples):
    """
    Write 1D signal from acquistion to h5 disk
    """

    # Write acquisition channel to h5 dset
    dset = r_grp[channelName]
    dset.resize(((i+1)*nSamples, 1))
    dset[i*nSamples:(i+1)*nSamples] = np.resize(channelSignal, (channelSignal.shape[0], 1))


def write_h5file(file_object, macAddress, dataAcquired, acqChannels, i, nSamples):
    """ 
    Utility function to open and write to a previously opened h5 file for the acquisition
    """

    # Create the datasets according to OpenSignals standard
    root_group_name = macAddress + '/'
    r_grp = file_object[root_group_name]

    # Digital
    for dgNr in xrange(0, 4):
        _write_acq_channel(r_grp, 'digital/digital_{}'.format(dgNr + 1),
                          dataAcquired[:, 1], i, nSamples)

    # Analog
    for chNr in acqChannels:
        _write_acq_channel(r_grp, 'raw/channel_{}'.format(chNr + 1),
                          dataAcquired[:, chNr + 5], i, nSamples)
        
    _write_acq_channel(r_grp, 'raw/nSeq', dataAcquired[:, 0], i, nSamples)


def open_h5file(path_to_save, macAddress, acqChannels, acqLabels, nSamples):
    """ 
    Utility function to open and setup a maximum 2 hours duration h5 file for the acquisition
    """

    # Open file
    filename = datetime.datetime.now().strftime("test_%Y-%m-%d_%H-%M-%S") + '.h5'
    file_path = os.path.join(path_to_save, filename)

    # Copy file 
    f = h5.File(file_path, 'w')

    # Create the datasets according to OpenSignals standard
    root_group_name = macAddress + '/'
    r_grp = f.create_group(root_group_name)

    # Digital
    for dgNr in xrange(0, 4):
        r_grp.create_dataset('digital/digital_{}'.format(dgNr + 1), 
                             dtype='uint16', shape=(nSamples, 1), 
                             maxshape=(2*60*60*nSamples, 1), chunks=(1024, 1))

    # Analog
    for chNr, chLabel in zip(acqChannels, acqLabels):
        ch_dset = r_grp.create_dataset('raw/channel_{}'.format(chNr + 1),
                              dtype='uint16', shape=(nSamples, 1), 
                              maxshape=(2*60*60*nSamples, 1), chunks=(1024, 1))
        ch_dset.attrs['label'] = chLabel
        ch_dset.attrs['sensor'] = 'RAW'
        ch_dset.attrs['special'] = '{}'

    # Sequence Number
    r_grp.create_dataset('raw/nSeq', dtype='uint16', 
                          shape=(nSamples, 1), 
                          maxshape=(2*60*60*nSamples, 1), chunks=(1024, 1))

    return f


def create_opensignals_mdata(f, setup, initialTimeAcquisition, i):
    """ 
    Utility function to close h5 file for the acquisition
    """

    # Set attributes for the file
    i_time_acq = initialTimeAcquisition
    nsamples = i*setup['nSamples']
    duration = '{}s'.format(nsamples/setup['samplingRate'])

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

    for k in attrs.keys():
        # Set attributes of the root group
        f[f.keys()[0]].attrs[k] = attrs[k]







