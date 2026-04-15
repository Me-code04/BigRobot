from machine import Pin, PWM
import utime

# ---------- PIN SETUP ----------
RPWM_PIN = 16
LPWM_PIN = 17
REN_PIN  = 18
LEN_PIN  = 19

PWM_FREQ = 1000   # start conservative; can raise later to 5000 or 20000

rpwm = PWM(Pin(RPWM_PIN))
lpwm = PWM(Pin(LPWM_PIN))
rpwm.freq(PWM_FREQ)
lpwm.freq(PWM_FREQ)

ren = Pin(REN_PIN, Pin.OUT)
len_ = Pin(LEN_PIN, Pin.OUT)

current = 0.0  # range -1.0 to +1.0

# ---------- HELPERS ----------
def _clamp(x, lo, hi):
    return max(lo, min(hi, x))

def _duty_u16(x):
    x = _clamp(x, 0.0, 1.0)
    return int(x * 65535)

def all_off():
    rpwm.duty_u16(0)
    lpwm.duty_u16(0)
    ren.value(0)
    len_.value(0)

def enable_driver():
    ren.value(1)
    len_.value(1)

def _stop_deadtime():
    rpwm.duty_u16(0)
    lpwm.duty_u16(0)
    ren.value(0)
    len_.value(0)
    utime.sleep_ms(20)
    ren.value(1)
    len_.value(1)

def _apply_speed_now(s):
    if abs(s) < 1e-6:
        all_off()
        return

    enable_driver()
    duty = _duty_u16(abs(s))

    if s > 0:
        lpwm.duty_u16(0)
        rpwm.duty_u16(duty)
    else:
        rpwm.duty_u16(0)
        lpwm.duty_u16(duty)

def set_speed(target, ramp_step=0.02, ramp_delay_ms=20, deadband=0.05):
    global current

    target = _clamp(target, -1.0, 1.0)
    if abs(target) < deadband:
        target = 0.0

    # add deadtime only if direction changes
    if current > 0 and target < 0:
        _stop_deadtime()
    elif current < 0 and target > 0:
        _stop_deadtime()

    start = current
    diff = target - start
    steps = max(1, int(abs(diff) / ramp_step))

    for i in range(1, steps + 1):
        s = start + diff * i / steps
        _apply_speed_now(s)
        current = s
        utime.sleep_ms(ramp_delay_ms)

    current = target

# ---------- TEST SEQUENCE ----------
all_off()
utime.sleep(1)

print("Forward 0.2")
set_speed(0.2)
utime.sleep(2)

print("Forward 0.4")
set_speed(0.4)
utime.sleep(2)

print("Stop")
set_speed(0.0)
utime.sleep(1)

print("Reverse 0.2")
set_speed(-0.2)
utime.sleep(2)

print("Stop")
set_speed(0.0)
all_off()