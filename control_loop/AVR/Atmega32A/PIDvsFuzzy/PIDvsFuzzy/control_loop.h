/*
 * control_loop.h
 *
 * Created: 28-Dec-18 15:22:33
 *  Author: uidq6025
 */ 


#ifndef CONTROL_LOOP_H_
#define CONTROL_LOOP_H_

#define REFRESH_RATE_MS 16.384

#define CONTROL_LOOP_NONE 0
#define CONTROL_LOOP_PID 1
#define CONTROL_LOOP_FUZZY 2

int TARGET_TICKS;

uint8_t CONTROL_LOOP;  // specifies desired control loop: PID or Fuzzy
uint16_t power_supply_voltage;

#endif /* CONTROL_LOOP_H_ */