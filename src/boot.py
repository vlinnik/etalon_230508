# This is script that run when device boot up or wake from sleep.
import network
from machine import Pin

sta = network.WLAN(0)
ap = network.WLAN(1)

try:
	eth = network.LAN(mdc=Pin(23),mdio=Pin(18),power=Pin(4),id=None,phy_addr=1,phy_type=network.PHY_LAN8720)
	eth.active(True)
except:
	pass

import webrepl
webrepl.start()

def reboot():
    import machine
    machine.reset()