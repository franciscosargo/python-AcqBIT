# Overview

## python-AcqBIT
The present set of modules implement a robust python application, for handling long-term acquisition of multiple BITalino devices running in the background. It is designed to save the acquisition data in HDF5 format in a specfic local directory, synchronizable with external servers by means of a 3-rd party application (Seafile).  

## Motivation
As the availibilty of open-source robust acquisition software for the BITalino board (see https://bitalino.com/en/ for more details), suitable for persavive bio-signal acquisition, is at best scarce, this projects provides a simple and yet efficient solution. Using python's multiprocessing module to handle multiple long-term concurent acquisitions, this prototypical application allows for the user to easily setup a multimodal continuos bio-signal monitorization, run it as a background process and promptly share the acquired signals via cloud synchronization, thus maximizing productivity.      

# Pre-Configured Installers

We have prepared user-friendly installers that already include a Python distribution with all the dependencies. The following instructions should guide you through the initial steps needed to reach a viable and repeatable configuration. For illustrative purposes, let's consider that the MAC address of your device is `01:23:45:67:89:AB`

## Windows

- Download and install ServerBIT: http://www.bitalino.com/downloads/ServerBIT_win64.zip
- Launch ServerBIT (a connection error message should appear on a command line window)
- Close the command line window 
- Go to your the `ServerBIT` directory on your home folder and edit `config.json`
- Replace the text `WINDOWS - XX:XX:XX:XX:XX:XX | MAC - /dev/tty.BITalino-XX-XX-DevB` by the MAC address of your device (the resulting line should be `"device": "01:23:45:67:89:AB"`)
- From now on whenever you launch ServerBIT it should automatically connect to your device and continuously stream data (to stop simply close the command line window)
- A configuration test can be made using the `ClientBIT.html` page found on the `ServerBIT` directory on your home folder

## Mac OS 

- Download and install ServerBIT: http://www.bitalino.com/downloads/ServerBIT.pkg
- Execute the ServerBIT_Launcher app to create the configurations folder
- Execute the ServerBIT_Killer app to stop the server
- Go to your the `ServerBIT` directory on your home folder and edit `config.json`
- Replace the text `WINDOWS - XX:XX:XX:XX:XX:XX | MAC - /dev/tty.BITalino-XX-XX-DevB` by the Virtual COM Port (VCP) address of your device (the resulting line should be `"device": "/dev/tty.BITalino-89-AB-DevB"`)
- From now on whenever you execute the ServerBIT_Launcher app it should automatically connect to your device and continuously stream data (to stop simply execute the ServerBIT_Killer app)
- A configuration test can be made using the `ClientBIT.html` page found on the `ServerBIT` directory on your home folder
- **IMPORTANT NOTICE:** Currently no visible feedback is provided on Mac OS... see the troubleshooting section bellow for a check list of potential problems


# Running from Sources

## Dependencies 

- Python 2.7 must be installed
- BITalino API and dependencies installed
- PySerial module installed
- Tornado module installed


## Testing ServerBIT

- Launch the `ServerBIT.py` script using your Python interpreter to create `ServerBIT` directory on your home folder and `config.json` file
- Edit `config.json` on a text editor and change the `device` property to the MAC address or Virtual COM port (VCP) of your BITalino device
- Launch the `ServerBIT.py` script using your Python interpreter
- Once a message similar to `LISTENING` appears in the console the server is ready to receive a connection
- Open `ClientBIT.html` on your web browser
- You should start to see the instruction call log on the page body and a real time signal corresponding to A1 on `ClientBIT.html`


# Settings in `config.json`

- `"device"`: MAC address or Virtual COM port (VCP) of your BITalino device
- `"channels"`: List of channels to be acquired from the device (e.g. [1, 6] acquires channels A1 and A6)
- `"sampling_rate"`: Sampling rate at which data should be acquired (i.e. 1000, 100, 10 or 1 Hz)
- `"port"`: Port through which ServerBIT will be streaming data
- `"labels"`: Human-readable descriptor associated with each channel acquired by the device, and that will be used to name the properties on the JSON-formatted structure created for streaming (**NOTE:** BITalino always sends a sequence number, two digital inputs and two digital outputs, hence the 5 first entries in the `"labels"` array)


# Troubleshooting

- Verify that your device is turned on... its one of the most common cause of problems :D
- Double check the `config.json` to confirm that the MAC address or Virtual COM port (VCP) of your BITalino device is correct and correctly formatted
- Make sure that the port listed on the `config.json` file matches the one on your client
- Depending on how you are accessing the server, confirm that the client is connecting to the correct IP address
- If your home folder has non-standard ASCII characters modifications to the ServerBIT source code may be needed
- Launch the `ServerBIT.py` script using a Python interpreter to obtain additional information about the error
- Post an issue in this repository and we'll try to support to the best of our abilities