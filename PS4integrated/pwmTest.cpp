#include "pwmTest.h"
#include <math.h>
#include "hardware/pwm.h"

static float clampf(float x, float lo, float hi) {
    if (x < lo) return lo;
    if (x > hi) return hi;
    return x;
}

static uint16_t duty_u16(float x) {
    x = clampf(x, 0.0f, 1.0f);
    return (uint16_t)(x * 65535.0f);
}

static void setup_pwm_pin(uint pin, uint pwm_freq) {
    gpio_set_function(pin, GPIO_FUNC_PWM);

    uint slice = pwm_gpio_to_slice_num(pin);
    uint32_t wrap = 65535;
    float clkdiv = 125000000.0f / ((wrap + 1) * pwm_freq);

    if (clkdiv < 1.0f) clkdiv = 1.0f;
    if (clkdiv > 255.0f) clkdiv = 255.0f;

    pwm_set_clkdiv(slice, clkdiv);
    pwm_set_wrap(slice, wrap);
    pwm_set_enabled(slice, true);
    pwm_set_gpio_level(pin, 0);
}

void motor_init(BTS7960Motor* m, uint rpwm, uint lpwm, uint ren, uint len, uint pwm_freq) {
    m->rpwm_pin = rpwm;
    m->lpwm_pin = lpwm;
    m->ren_pin = ren;
    m->len_pin = len;
    m->current_speed = 0.0f;

    setup_pwm_pin(m->rpwm_pin, pwm_freq);
    setup_pwm_pin(m->lpwm_pin, pwm_freq);

    gpio_init(m->ren_pin);
    gpio_set_dir(m->ren_pin, GPIO_OUT);

    gpio_init(m->len_pin);
    gpio_set_dir(m->len_pin, GPIO_OUT);

    motor_all_off(m);
}

void motor_all_off(BTS7960Motor* m) {
    pwm_set_gpio_level(m->rpwm_pin, 0);
    pwm_set_gpio_level(m->lpwm_pin, 0);
    gpio_put(m->ren_pin, 0);
    gpio_put(m->len_pin, 0);
}

void motor_enable_driver(BTS7960Motor* m) {
    gpio_put(m->ren_pin, 1);
    gpio_put(m->len_pin, 1);
}

void motor_stop_deadtime(BTS7960Motor* m, uint deadtime_ms) {
    pwm_set_gpio_level(m->rpwm_pin, 0);
    pwm_set_gpio_level(m->lpwm_pin, 0);
    gpio_put(m->ren_pin, 0);
    gpio_put(m->len_pin, 0);
    sleep_ms(deadtime_ms);
    gpio_put(m->ren_pin, 1);
    gpio_put(m->len_pin, 1);
}

void motor_apply_speed_now(BTS7960Motor* m, float s) {
    if (fabsf(s) < 1e-6f) {
        motor_all_off(m);
        return;
    }

    motor_enable_driver(m);
    uint16_t duty = duty_u16(fabsf(s));

    if (s > 0.0f) {
        pwm_set_gpio_level(m->lpwm_pin, 0);
        pwm_set_gpio_level(m->rpwm_pin, duty);
    } else {
        pwm_set_gpio_level(m->rpwm_pin, 0);
        pwm_set_gpio_level(m->lpwm_pin, duty);
    }
}

void motor_set_speed(BTS7960Motor* m, float target,
                     float ramp_step,
                     uint ramp_delay_ms,
                     float deadband,
                     uint deadtime_ms) {
    if (target < -1.0f) target = -1.0f;
    if (target > 1.0f) target = 1.0f;

    if (fabsf(target) < deadband) {
        target = 0.0f;
    }

    if (m->current_speed > 0.0f && target < 0.0f) {
        motor_stop_deadtime(m, deadtime_ms);
    } else if (m->current_speed < 0.0f && target > 0.0f) {
        motor_stop_deadtime(m, deadtime_ms);
    }

    float start = m->current_speed;
    float diff = target - start;
    int steps = (int)(fabsf(diff) / ramp_step);
    if (steps < 1) steps = 1;

    for (int i = 1; i <= steps; i++) {
        float s = start + diff * ((float)i / (float)steps);
        motor_apply_speed_now(m, s);
        m->current_speed = s;
        sleep_ms(ramp_delay_ms);
    }

    m->current_speed = target;
}