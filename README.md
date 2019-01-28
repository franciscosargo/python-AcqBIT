# Overview

## python-AcqBIT
The present set of modules implement a robust python application, for handling long-term acquisition of multiple BITalino devices running in the background. It is designed to save the acquisition data in HDF5 format in a specfic local directory, synchronizable with external servers by means of a 3-rd party application (Seafile).  

## Motivation
As the availibilty of open-source robust acquisition software for the BITalino board (see https://bitalino.com/en/ for more details), suitable for persavive bio-signal acquisition, is at best scarce, this projects provides a simple and yet efficient solution. Using python's multiprocessing module to handle multiple long-term concurent acquisitions, this prototypical application allows for the user to easily setup a multimodal continuos bio-signal monitorization, run it as a background process and promptly share the acquired signals via cloud synchronization, thus maximizing productivity.      

# Running from Sources

## Dependencies 
- Python 2.7 must be installed
- BITalino API and dependencies installed
- PySerial module installed
- Tornado module installed
