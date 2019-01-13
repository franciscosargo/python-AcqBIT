import sys
from cx_Freeze import setup, Executable


build_exe_options = {"packages": ["os",
                                  "pickle",
                                  "time",
                                  "multiprocessing", 
                                  "bitalino",
                                  "pystray",
                                  "PIL"],
                    'includes':['atexit', 'numpy.core._methods', 'numpy.lib.format'],
                       
                    }


base= None
if sys.platform == "win32":
    base = "Console"


setup(name = "My Application",
      version = "0.1",
      description = "My example application",
      options = {"build_exe": build_exe_options},
      executables = {Executable("application.py", base=base)})