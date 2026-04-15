#ifndef PWM_TEST_H
#define PWM_TEST_H

#include "pico/stdlib.h"

struct BTS7960Motor {
    uint rpwm_pin;
    uint lpwm_pin;
    uint ren_pin;
    uint len_pin;
    float current_speed;   // -1.0 to +1.0
};

void motor_init(BTS7960Motor* m, uint rpwm, uint lpwm, uint ren, uint len, uint pwm_freq = 1000);
void motor_all_off(BTS7960Motor* m);
void motor_enable_driver(BTS7960Motor* m);
void motor_stop_deadtime(BTS7960Motor* m, uint deadtime_ms = 20);
void motor_apply_speed_now(BTS7960Motor* m, float s);
void motor_set_speed(BTS7960Motor* m, float target,
                     float ramp_step = 0.02f,
                     uint ramp_delay_ms = 20,
                     float deadband = 0.05f,
                     uint deadtime_ms = 20);

#endif