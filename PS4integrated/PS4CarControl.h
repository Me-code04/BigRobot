#ifndef PS4_CAR_CONTROL_H
#define PS4_CAR_CONTROL_H

#include "bluepad32/bluepad32.h"
#include "pwmTest.h"

void setupControllerCallbacks();
void processController(BTS7960Motor* motor);

#endif