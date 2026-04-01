import pygame
import requests
import time

PICO_IP = "192.168.1.123"   # change to your Pico W IP
URL = f"http://{PICO_IP}/control"

SEND_INTERVAL = 0.05   # seconds

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    raise RuntimeError("No Xbox controller detected.")

controller = pygame.joystick.Joystick(0)
controller.init()

print("Connected controller:", controller.get_name())

def deadzone(value, dz=0.08):
    if abs(value) < dz:
        return 0.0
    return value

last_send = 0

while True:
    pygame.event.pump()

    # Common Xbox mapping in pygame
    # axis 0 = left stick X
    # axis 1 = left stick Y
    steering = deadzone(controller.get_axis(0))
    throttle = -deadzone(controller.get_axis(1))  # up = forward

    now = time.time()
    if now - last_send >= SEND_INTERVAL:
        try:
            requests.get(
                URL,
                params={
                    "throttle": round(throttle, 3),
                    "steering": round(steering, 3)
                },
                timeout=0.1
            )
            print(f"Throttle={throttle:.2f}, Steering={steering:.2f}")
        except Exception as e:
            print("Send failed:", e)

        last_send = now

    time.sleep(0.01)