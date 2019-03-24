import sys
import os
from cx_Freeze import setup, Executable

# modules to include in build
# 'numpy.core._methods', 'numpy.lib.format'

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"includes": ['UserList', 'UserString'],
                     "packages":['numpy', 'bluetooth', 'PIL'],
                     "include_files": ['BITALINO-logo.png', 'config.json', 'add_ons/'],
                     "include_msvcr": True}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None

setup(name = "acqBIT",
      version = "2.0",
      description = ("Application for robust pervasive bio-signals", 
                      "acquisition with BITalino devices"),
      options = {"build_exe": build_exe_options},
      executables = [Executable("application.py")])