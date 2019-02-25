import sys
import os
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"includes": ['numpy.core._methods', 'numpy.lib.format', 'UserList', 'UserString'],
                     "packages":['pystray', 'PIL'],
                     "include_files": ['BITALINO-logo.png', 'config.json'],
                     "include_msvcr": True}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None


setup(name = "acqBIT",
      version = "2.0",
      description = "Application for robust pervasive bio-signals acquisition with BITalino devices",
      options = {"build_exe": build_exe_options},
      executables = [Executable("application.py")])