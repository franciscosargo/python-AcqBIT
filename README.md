# Overview

## python-AcqBIT
The present set of modules implements a python application for long-term robust acquisition of multiple BITalino devices running as backgroud processes.

The application saves the acquisition data in HDF5 format in a specific local directory, synchronizable with external servers by means of a 3rd party application (Seafile).  

## Motivation
The availabilty of open-source robust acquisition software for the BITalino board (see https://bitalino.com/en/ for more details), suitable for pervasive bio-signal acquisition, is at best scarce. 

This projects provides a simple and yet efficient solution: by using python's multiprocessing module to handle multiple long-term concurent acquisitions, this prototypical application allows for the user to easily setup a multimodal continuos bio-signal monitorization, run it in several background processes and promptly share the produced data via cloud synchronization.      

# Configuration
The acquisition is governed by the use of a configuration file in .json format. The strucuture presents two main fields: `"device"`, holding the metadata for the specifications of the device during acquisition, and `"user"`, for insertion of a suitable username under which to group the acquisition files. 
 
## Settings in `config.json`
- `"device"`: MAC address or Virtual COM port (VCP) of your BITalino device
- `"channels"`: List of channels to be acquired from the device (e.g. [1, 6] acquires channels A1 and A6)
- `"sampling_rate"`: Sampling rate at which data should be acquired (i.e. 1000, 100, 10 or 1 Hz)
- `"labels"`: Human-readable descriptor associated with each channel acquired by the device, and that will be used to name the properties on the JSON-formatted structure created for streaming (**NOTE:** BITalino always sends a sequence number, two digital inputs and two digital outputs, hence the 5 first entries in the `"labels"` array)

# Running from Sources

##  Dependencies 
- Python 2.7 must be installed
- BITalino API and dependencies installed
- Pystray module installed
- Pillow module installed

## PIP Installation
The simplest installation procedure from source is to use pip, the PyPA recommended tool for installing Python packages. 
The required packages are summarized in the following list:
```bash
bitalino==1.2.1
h5py==2.9.0
numpy==1.16.0
Pillow==5.4.1
pystray==0.14.4
```
The packages can be duly installed by runnig:
```bash
pip install requirements.txt
```
## Bluetooth module Installation

### Windows

## Main Application
To run the main application, provided the configuration is correct, simply type:
```bash
python application.py
```

# Running from Builds




