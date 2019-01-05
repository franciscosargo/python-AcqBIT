
from bitalino import BITalino


if __name__ == '__main__':

    ## Choose Path Name
    path_name = 'C:\Users\franciscosargo\Desktop'
    macAddress = "20:16:04:12:01:23"
    
    # Set Characteristics of the acquisition
    batteryThreshold = 30
    acqChannels = [0,3]
    samplingRate = 1000
    nSamples = 1000
    digitalOutput = [0,0,1,1]
    
    while True:
        ## Connection Loop
        while True:
            try:
                device = BITalino(macAddress)  # Connect to BITalino
                print device.version()
                break
            except Exception as e:
                print e
                pass
                
        # Start Acquisition
        device.start(samplingRate, acqChannels)
        
        # Acquisition Loop
        while True:
            try:
                device.read(nSamples)
                
            except Exception as e:
                print e
                device.stop()
                device.close()
                break
        

    
    
  