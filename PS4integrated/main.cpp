#include <stdio.h>
#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"

#include "PS4CarControl.h"
#include "pwmTest.h"

static const uint RPWM_PIN = 16;
static const uint LPWM_PIN = 17;
static const uint REN_PIN  = 18;
static const uint LEN_PIN  = 19;
static const uint PWM_FREQ = 1000;

BTS7960Motor testMotor;

int main() {
    stdio_init_all();

    if (cyw43_arch_init()) {
        printf("CYW43 init failed\n");
        return 1;
    }

    motor_init(&testMotor, RPWM_PIN, LPWM_PIN, REN_PIN, LEN_PIN, PWM_FREQ);
    setupControllerCallbacks();

    printf("Waiting for PS4 controller...\n");
    printf("Hold SHARE + PS to pair\n");

    while (true) {
        processController(&testMotor);
        sleep_ms(20);
    }

    return 0;
}