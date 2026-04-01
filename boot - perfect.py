from dc import DCMotor
from machine import Pin, PWM
import time
import network
import BlynkLib

frequency = 1000

pin1 = Pin(3, Pin.OUT)
pin2 = Pin(4, Pin.OUT)
enable1 = PWM(Pin(2))
enable1.freq(frequency)

pin3 = Pin(6, Pin.OUT)
pin4 = Pin(7, Pin.OUT)
enable2 = PWM(Pin(5))
enable2.freq(frequency)

pin5 = Pin(9, Pin.OUT)
pin6 = Pin(10, Pin.OUT)
enable3 = PWM(Pin(8))
enable3.freq(frequency)

pin7 = Pin(12, Pin.OUT)
pin8 = Pin(13, Pin.OUT)
enable4 = PWM(Pin(11))
enable4.freq(frequency)

dc_motor1 = DCMotor(pin1, pin2, enable1)
dc_motor2 = DCMotor(pin3, pin4, enable2)
dc_motor3 = DCMotor(pin5, pin6, enable3)
dc_motor4 = DCMotor(pin7, pin8, enable4)

# Set min duty cycle (15000) and max duty cycle (65535) 
#dc_motor = DCMotor(pin1, pin2, enable, 15000, 65535)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("KnoxTronics","AsDfGW2481632")
 
BLYNK_AUTH = "w2HxlAUKH_-rWy496L9Oj_BZBqzU_q82"
 
# connect the network       
wait = 10
while wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    wait -= 1
    print('waiting for connection...')
    time.sleep(1)
 
# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    ip=wlan.ifconfig()[0]
    print('IP: ', ip)
    
 
#"Connection to Blynk"
# Initialize Blynk
blynk = BlynkLib.Blynk(BLYNK_AUTH)
 
# Register virtual pin handler

def Forward():
    print('Forward')
    dc_motor1.forward()
    dc_motor2.forward()
    dc_motor3.forward()    
    dc_motor4.forward()    
    
def Backward():
    print('Backward')
    dc_motor1.backward()
    dc_motor2.backward()
    dc_motor3.backward()
    dc_motor4.backward()
    
def Left():
    print('Left')
    dc_motor2.forward()
    dc_motor4.forward()
    dc_motor1.backward()
    dc_motor3.backward()
    
def Right():
    print('Right')
    dc_motor1.forward()
    dc_motor3.forward()
    dc_motor2.backward()
    dc_motor4.backward()

def Stop():
    dc_motor1.stop()
    dc_motor2.stop()
    dc_motor3.stop()
    dc_motor4.stop()

@blynk.on("V0") #virtual pin V0
def v0_write_handler(value): #read the value
    if int(value[0]) == 1:
        print("ON")
        Forward()
    else:
        print("OFF")
        Stop()
        
@blynk.on("V1") #virtual pin V1
def v1_write_handler(value): #read the value
    if int(value[0]) == 1:
        print("ON")
        Backward()
    else:
        print("OFF")
        Stop()

@blynk.on("V2") #virtual pin V2
def v2_write_handler(value): #read the value
    if int(value[0]) == 1:
        print("ON")
        Right()
    else:
        print("OFF")
        Stop()
        
@blynk.on("V3") #virtual pin V3
def v3_write_handler(value): #read the value
    if int(value[0]) == 1:
        print("ON")
        Left()
    else:
        print("OFF")
        Stop()
        
@blynk.on("V4") #virtual pin V4
def v4_write_handler(value): #read the value
    if int(value[0]) == 1:
        print("ON")
        Stop()
    else:
        print("OFF")
        Stop()

while True:
    blynk.run()

