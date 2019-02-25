
![alt text](https://raw.githubusercontent.com/franciscosargo/python-AcqBIT/master/add_ons/acqBIT.PNG)

# Overview

## python-AcqBIT
The present set of modules implements a python application for long-term robust acquisition of multiple BITalino devices running as backgroud processes.

The application saves the acquisition data in HDF5 format in a specific local directory, synchronizable with external servers by means of a 3rd party application (Seafile).  

## Motivation
The availabilty of open-source robust acquisition software for the BITalino board (see https://bitalino.com/en/ for more details), suitable for pervasive bio-signal acquisition, is at best scarce. 

This projects provides a simple and yet efficient solution: by using python's multiprocessing module to handle multiple long-term concurent acquisitions, this prototypical application allows for the user to easily setup a multimodal continuos bio-signal monitorization, run it in several background processes and promptly share the produced data via cloud synchronization.      

# Configuration
The acquisition is governed by the use of a configuration file in .json format. The strucuture presents two main fields: `"device"`, holding the metadata for the specifications of device acquisition, and `"user"`, holding a suitable username under which to group the acquisition files. 
 
## Settings in `config.json`
Each entry within the `"device"` field is a .json substructure, with key equal to the MAC address or Virtual COM port (VCP) of your BITalino device. Each entry should thus be inserted in the form `WINDOWS/Linux - XX:XX:XX:XX:XX:XX | MAC - /dev/tty.BITalino-XX-XX-DevB`, depending on your platform.

The respective substructure of the `"device"` holds the following subfields:
- `"acqChannels"`: List of analog channels to be acquired from the device (e.g. [1, 6] acquires channels A1 and A6)
- `"samplingRate"`: Sampling rate at which data should be acquired (i.e. 1000, 100, 10 or 1 Hz)
- `"acqLabels"`: Human-readable descriptor associated with each channel acquired by the device, and that will be used to name the properties on the JSON-formatted structure created for streaming (**NOTE:** BITalino always sends a sequence number, two digital inputs and two digital outputs, hence the 5 first entries in the `"labels"` array)
- `master`: Either `True` or `False`, being the flag denoting if the current device is master synchronizer or not.  (**NOTE:** Only one device should be master.)
- `"syncInterval`: The interval in minutes between each module acquistion synchronization, with the triggering of the digital channels of the master device (**NOTE:** Only value in the master device is considered.).
- `"resolution"`: Resolution for each of the acquisition channels as specified in the field `"acqLabels"`.
- `"nSamples"`: Number of samples read from a running BITalino device within each iteration of the acquisition.
- `"deviceName`: Human readable device name, useful for posterior indentification.
- `"macAddress`: MAC address or Virtual COM port (VCP) of BITalino device.

# Running from Sources
In order to run the project from source, the installation of necessary dependencies is required. Hence, since some of the dependencies are Python packages, the procedure may alter your current Python environment adding new or reinstalling existing packages. The creation of a fresh environment, preferably already bundled with `pip`, is advisable. 

##  Dependencies 
- Python 2.7 must be installed
- Python Bluetooth extension package installed (not required by Mac OS)
- BITalino API and dependencies installed
- Pystray module installed
- Pillow module installed

## 1. Bluetooth Extension Installation
In order to gain access to Python's Bluetooth capabilities, it is necessary to install specific extensions for each platform.

### Windows
PyBluez serves as the best Bluetooth Python extension package for Windows. Since the package is not available in the repositories maintained by PyPA, the best current method of installation is to use the package provided by the Anaconda Cloud. This requires the creation of a new conda environment, after the installation of the Anaconda distribution, which can be found at: https://repo.continuum.io/archive/Anaconda2-2018.12-Windows-x86_64.exe).
 
Following the activation of an appropriate conda environment, the installation of the package can proceed by typing in a shell:
 ```bash
conda install -c slobodan pybluez
```

### GNU/Linux
On Linux systems the procedure is simpler, only requiring the following `bash` commands:
 ```bash
sudo apt-get install libbluetooth-dev
pip install pybluez
```

## 2. Core Packages Installation
To continue the installation process, clone or download the present repository into your machine. The simplest installation procedure from source is to use pip, the PyPA recommended tool for installing Python packages.
The required packages are summarized in the following list:
```bash
bitalino==1.2.1
h5py==2.9.0
numpy==1.16.0
Pillow==5.4.1
pystray==0.14.4
```

The packages can be duly installed via command line by runnig:
```bash
cd PROJECTFOLDERPATH/python-AcqBIT
pip install -r requirements.txt
```

## 3. Deployment of Main Application
To run the main application, provided the configuration is correct, simply type:
```bash
python application.py
```

# (Optional) File Synchronization via Seafile
Synchronization of the files produced by the application can be done resorting to the seafile platform. 
It is intedend to synchronized the local acqBIT folder with the remote present the server 

## 1. Download Seafile Desktop Syncing Client
The Seafile Desktop Syncing Client is a client side application that allows the user to synchronize any local folder to a remote server. 
The installation method varies across different platforms. 

### Windows
https://download.seadrive.org/seafile-6.2.11-en.msi

### Linux
https://help.seafile.com/en/syncing_client/install_linux_client.html

### Mac OS
https://download.seadrive.org/seafile-client-6.2.11.dmg


## 2. Login with Credentials
After download and installation of the client, launch the program and click `Add an account`. Then fill in the following fields:

```
   server: http://193.136.222.123:8000
   Email/Username: (your email/username)
   Password: (your password)
   Computer Name: (your computer name)
``` 
   
## 3. Sync acqBIT Folder
After Login, look for the acqBIT library under `My Libraries`. If present, simply right click on the library icon and sync it with the local acqBIT folder created by the acquistion application.

If there is no acqBIT library, simply drag and drop the local acqBIT folder in the bottommost field dubbed `Drop Folder to Sync`.



