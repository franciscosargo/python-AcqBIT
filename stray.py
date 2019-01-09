from pystray import MenuItem as item
import pystray
from PIL import Image

def stop():
    icon.stop()

def action():
    pass

image = Image.open("BITALINO-logo.png")
menu = [item('stop', stop), item('name', action)]
icon = pystray.Icon("name", image, "title", menu)

        