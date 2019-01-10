"""
 * \author     Francisco Sargo
 * \version    1.0
 * \date       January 2019
 * 
 * \section LICENSE
 
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Lesser General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Lesser General Public License for more details.
 
 You should have received a copy of the GNU Lesser General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
 
"""

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

        