from machine import Pin, PWM
import utime

# ---------- PIN SETUP ----------
RPWM_PIN = 16
LPWM_PIN = 17
REN_PIN  = 18   # R_RN / R_EN
LEN_PIN  = 19   # L_RN / L_EN

FREQ = 20000  # try 5000 if 20 kHz is unstable

rpwm = PWM(Pin(RPWM_PIN))
lpwm = PWM(Pin(LPWM_PIN))
rpwm.freq(FREQ)
lpwm.freq(FREQ)

ren = Pin(REN_PIN, Pin.OUT)
len_ = Pin(LEN_PIN, Pin.OUT)

# Track current speed command
current = 0.0  # range [-1.0, 1.0]

# ---------- HELPERS ----------
def _duty_u16(x: float) -> int:
    x = max(0.0, min(1.0, x))
    return int(x * 65535)

def all_off():
    ren.value(0)
    len_.value(0)
    rpwm.duty_u16(0)
    lpwm.duty_u16(0)

def _set_forward(duty: int):
    len_.value(0)
    lpwm.duty_u16(0)
    ren.value(1)
    rpwm.duty_u16(duty)

def _set_reverse(duty: int):
    ren.value(0)
    rpwm.duty_u16(0)
    len_.value(1)
    lpwm.duty_u16(duty)

def _stop_with_deadtime():
    all_off()
    utime.sleep_us(300)

def _apply_speed_now(s: float):
    global current

    if abs(s) < 1e-6:
        all_off()
        return

    duty = _duty_u16(abs(s))

    # If direction changes, stop briefly first
    if current > 0 and s < 0:
        _stop_with_deadtime()
    elif current < 0 and s > 0:
        _stop_with_deadtime()

    if s > 0:
        _set_forward(duty)
    else:
        _set_reverse(duty)

def set_speed(target: float, ramp_step=0.02, ramp_delay_ms=15, deadband=0.05):
    global current

    target = max(-1.0, min(1.0, target))
    if abs(target) < deadband:
        target = 0.0

    diff = target - current
    steps = max(1, int(abs(diff) / ramp_step))

    start = current
    for i in range(1, steps + 1):
        s = start + diff * i / steps
        _apply_speed_now(s)
        current = s
        utime.sleep_ms(ramp_delay_ms)

    current = target

# ---------- DEMO ----------
all_off()
utime.sleep(1)

print("Forward 0.4")
set_speed(0.4)
utime.sleep(2)

print("Forward 0.8")
set_speed(0.8)
utime.sleep(2)

print("Stop")
set_speed(0.0)
utime.sleep(1)

print("Reverse 0.4")
set_speed(-0.4)
utime.sleep(2)

print("Stop")
set_speed(0.0)
all_off()