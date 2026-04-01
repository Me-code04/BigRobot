import network

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
mac = wlan.config('mac')
print(':'.join('%02x' % b for b in mac))

# MAC Address 28:cd:c1:06:8c:5b