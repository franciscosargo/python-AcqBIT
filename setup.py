import sys
import os
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os", "bitalino", "multiprocessing",
                                 "json", "numpy", "pystray", "datetime", 
                                 "PIL", "serial", "UserList", "UserString"],
                     "include_files": ['BITALINO-logo.png', 'config.json'],
                     "include_msvcr": True}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
#if sys.platform == "win32":
    #base = "Win32GUI"

setup(name = "acqBIT",
      version = "0.1",
      description = "Application for robust pervasive bio-signals acquisition with BITalino devices",
      options = {"build_exe_options": build_exe_options},
      executables = [Executable("application.py",
                                shortcutName="acqBIT",
                                shortcutDir="StartupFolder",
                                base=base)])