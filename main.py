import network
import socket
import utime
from machine import Pin, PWM

# =========================
# WIFI SETTINGS
# =========================
SSID = "YOUR_WIFI_NAME"
PASSWORD = "YOUR_WIFI_PASSWORD"

# =========================
# MOTOR DRIVER PINS
# =========================
RPWM_PIN = 16
LPWM_PIN = 17
REN_PIN  = 18   # R_RN
LEN_PIN  = 19   # L_RN

# Optional steering servo
STEER_PIN = 15

# =========================
# SETUP WIFI
# =========================
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

print("Connecting to Wi-Fi...")
while not wlan.isconnected():
    utime.sleep(1)

ip = wlan.ifconfig()[0]
print("Connected. Pico W IP:", ip)

# =========================
# PWM SETUP
# =========================
rpwm = PWM(Pin(RPWM_PIN))
lpwm = PWM(Pin(LPWM_PIN))
rpwm.freq(20000)
lpwm.freq(20000)

ren = Pin(REN_PIN, Pin.OUT)
len_ = Pin(LEN_PIN, Pin.OUT)

steer_pwm = PWM(Pin(STEER_PIN))
steer_pwm.freq(50)

last_command_ms = utime.ticks_ms()

# =========================
# HELPERS
# =========================
def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def duty_u16(x):
    x = clamp(x, 0.0, 1.0)
    return int(x * 65535)

def all_off():
    ren.value(0)
    len_.value(0)
    rpwm.duty_u16(0)
    lpwm.duty_u16(0)

def set_throttle(t):
    t = clamp(t, -1.0, 1.0)

    if abs(t) < 0.05:
        all_off()
        return

    d = duty_u16(abs(t))

    # dead time
    ren.value(0)
    len_.value(0)
    rpwm.duty_u16(0)
    lpwm.duty_u16(0)
    utime.sleep_us(200)

    if t > 0:
        len_.value(0)
        lpwm.duty_u16(0)
        ren.value(1)
        rpwm.duty_u16(d)
    else:
        ren.value(0)
        rpwm.duty_u16(0)
        len_.value(1)
        lpwm.duty_u16(d)

def servo_us(us):
    us = clamp(us, 1000, 2000)
    duty = int(us * 65535 / 20000)
    steer_pwm.duty_u16(duty)

def set_steering(s):
    s = clamp(s, -1.0, 1.0)
    center = 1500
    span = 350
    pulse = int(center + s * span)
    servo_us(pulse)

# =========================
# SERVER
# =========================
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
server = socket.socket()
server.bind(addr)
server.listen(1)

print("Listening on", addr)

all_off()
set_steering(0)

while True:
    # failsafe
    if utime.ticks_diff(utime.ticks_ms(), last_command_ms) > 500:
        all_off()

    client, client_addr = server.accept()
    request = client.recv(1024).decode()

    try:
        line = request.split("\r\n")[0]
        path = line.split(" ")[1]

        throttle = 0.0
        steering = 0.0

        if path.startswith("/control?"):
            query = path.split("?", 1)[1]
            pairs = query.split("&")

            values = {}
            for pair in pairs:
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    values[k] = v

            if "throttle" in values:
                throttle = float(values["throttle"])
            if "steering" in values:
                steering = float(values["steering"])

            set_throttle(throttle)
            set_steering(steering)
            last_command_ms = utime.ticks_ms()

            response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nOK"
        else:
            response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nPico car ready"

    except Exception as e:
        all_off()
        response = "HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/plain\r\n\r\n" + str(e)

    client.send(response)
    client.close()