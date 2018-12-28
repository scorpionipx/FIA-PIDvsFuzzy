/*
 * global.h
 *
 * Created: 24-Nov-18 17:08:59
 *  Author: ScorpionIPX
 */ 


#ifndef GLOBAL_H_
#define GLOBAL_H_

#include <avr/io.h>
#define F_CPU 16000000UL

volatile int INT0_CNT;
volatile int TIMER0_CNT;
volatile int dummy;


volatile int REVOLUTIONS;
volatile int REVOLUTIONS_PER_MINUTE;


#endif /* GLOBAL_H_ */