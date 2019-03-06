# -*- coding: utf-8 -*-
"""
General utilities module. Used to implement context managers to deal with exceptions
on IO operations for file handling (implemented in ioopensignals) 
socket handlin (in case of interface).
"""


import socket
from contextlib import contextmanager


@contextmanager
def socketcontext(*args, **kw):
    s = socket.socket(*args, **kw)
    try:
        yield s
    finally:
        s.close()
