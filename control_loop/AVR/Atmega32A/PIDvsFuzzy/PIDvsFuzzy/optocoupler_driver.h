/*
 * optocoupler_driver.h
 *
 * Created: 28-Dec-18 16:34:43
 *  Author: uidq6025
 */ 


#ifndef OPTOCOUPLER_DRIVER_H_
#define OPTOCOUPLER_DRIVER_H_

#define TICKS_PER_REVOLUTION 660

volatile int TICKS;

void init_optocoupler(void);

#endif /* OPTOCOUPLER_DRIVER_H_ */