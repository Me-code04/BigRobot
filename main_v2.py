from BigRobot.dcmotor import DCMotor
from machine import Pin, PWM
from time import sleep

frequency = 1000

pin1 = Pin(3, Pin.OUT)
pin2 = Pin(4, Pin.OUT)
enable1 = PWM(Pin(2), frequency)

pin3 = Pin(6, Pin.OUT)
pin4 = Pin(7, Pin.OUT)
enable2 = PWM(Pin(5), frequency)

pin5 = Pin(9, Pin.OUT)
pin6 = Pin(10, Pin.OUT)
enable3 = PWM(Pin(8), frequency)

pin7 = Pin(12, Pin.OUT)
pin8 = Pin(13, Pin.OUT)
enable4 = PWM(Pin(11), frequency)

dc_motor1 = DCMotor(pin1, pin2, enable1)
dc_motor2 = DCMotor(pin3, pin4, enable2)
dc_motor3 = DCMotor(pin5, pin6, enable3)
dc_motor4 = DCMotor(pin7, pin8, enable4)

# Set min duty cycle (15000) and max duty cycle (65535) 
#dc_motor = DCMotor(pin1, pin2, enable, 15000, 65535)

def Forward():
    print('Forward')
    dc_motor12.forward(75)
    dc_motor3.forward(75)
    dc_motor4.forward(75)    

def Backward():
    print('Backward')
    dc_motor12.backwards(60)
    dc_motor3.backwards(60)
    dc_motor4.backwards(60)
    
def Left():
    print('Left')
    dc_motor12.forward(20)
    dc_motor3.forward(50)
    dc_motor4.backwards(50)
    
def Right(speed_percent):
    print('Right')
    dc_motor12.forward(20)
    dc_motor3.backwards(50)
    dc_motor4.forward(50)

def Stop():
    dc_motor12.stop()
    dc_motor3.stop()
    dc_motor4.stop()
    
try:
    Forward(50)
    sleep(5)
    Stop()
    sleep(5)
    
    Left(25)
    sleep(5)
    Stop()
    sleep(5)
    
    Backward(100)
    sleep(5)
    Right(25)
    sleep(5)
    Stop()
    sleep(5)
    
    Forward(5)
    sleep(5)
    Stop()
    
    Forward(50)
    sleep(5)
    Stop()
    
except KeyboardInterrupt:
    print('Keyboard Interrupt')
    dc_motor.stop()
