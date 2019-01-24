import sys
import os
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os", "bitalino", "multiprocessing",
                                 "json", "numpy", "pystray", "datetime", 
                                 "PIL", "serial", "UserList", "UserString"],

                     "exclude":["sqlite3"],
                     "include_files": [os.path.join(sys.prefix, 'DLLs', 'sqlite3.dll')]}

sys.path.append('C:\ProgramData\Anaconda2\DLLs')
#print [f for f in sys.path if 'DLL' in f]
#print sys.base_prefix

bdist_msi_options = {"packages": ["os", "bitalino", "multiprocessing",
                                 "json", "numpy", "pystray", "datetime", 
                                 "PIL", "serial", "UserList", "UserString"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
#if sys.platform == "win32":
    #base = "Win32GUI"

setup(  name = "acqBIT",
        version = "0.1",
        description = "Application for robust pervasive bio-signals acquisition with BITalino devices",
        options = {"bdist_msi": bdist_msi_options, "build_exe_options": build_exe_options},
        executables = [Executable("application.py",
                                  shortcutName="acqBIT",
                                  shortcutDir="StartupFolder",
                                  base=base)])