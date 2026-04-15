#include "PS4CarControl.h"
#include <stdio.h>
#include <math.h>

static GamepadPtr myGamepad = nullptr;

static float clampf(float x, float lo, float hi) {
    if (x < lo) return lo;
    if (x > hi) return hi;
    return x;
}

void onConnectedGamepad(GamepadPtr gp) {
    if (!myGamepad) {
        myGamepad = gp;
        printf("PS4 controller connected\n");
    }
}

void onDisconnectedGamepad(GamepadPtr gp) {
    if (gp == myGamepad) {
        myGamepad = nullptr;
        printf("Controller disconnected\n");
    }
}

void setupControllerCallbacks() {
    bp32_setup(&onConnectedGamepad, &onDisconnectedGamepad);
    bp32_forget_bluetooth_keys();   // use during pairing/testing
}

void processController(BTS7960Motor* motor) {
    bp32_update();

    if (!myGamepad || !myGamepad->isConnected()) {
        motor_set_speed(motor, 0.0f);
        return;
    }

    // R2 forward, L2 reverse
    float r2 = myGamepad->throttle() / 1023.0f;
    float l2 = myGamepad->brake() / 1023.0f;

    r2 = clampf(r2, 0.0f, 1.0f);
    l2 = clampf(l2, 0.0f, 1.0f);

    float speed = r2 - l2;

    // speed modes
    float speed_scale = 0.60f;
    if (myGamepad->a()) speed_scale = 0.35f;
    if (myGamepad->b()) speed_scale = 1.00f;

    speed *= speed_scale;

    // emergency stop
    if (myGamepad->x()) {
        speed = 0.0f;
    }

    motor_set_speed(motor, speed, 0.03f, 10, 0.04f, 20);

    printf("R2=%.2f L2=%.2f speed=%.2f\n", r2, l2, speed);
}