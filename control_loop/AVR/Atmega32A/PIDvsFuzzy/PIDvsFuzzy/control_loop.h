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

#define MAX_TARGET_TICKS 55
#define MIN_TARGET_TICKS 0

#define CONTROL_LOOP_START_FLAG_LENGTH 5
#define CONTROL_LOOP_START_FLAG_VALUE 35

int TARGET_TICKS;
unsigned char CONTROL_LOOP_START_FLAG;

uint8_t CONTROL_LOOP;  // specifies desired control loop: PID or Fuzzy
uint16_t power_supply_voltage;

void init_control_loop(void);

#endif /* CONTROL_LOOP_H_ */