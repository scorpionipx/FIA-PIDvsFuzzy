/*
 * optocoupler_driver.c
 *
 * Created: 28-Dec-18 16:34:30
 *  Author: uidq6025
 */ 

#include "global.h"
#include "optocoupler_driver.h"


void init_optocoupler(void)
{
	INT0_CNT = 0;
	REVOLUTIONS = 0;
	TICKS = 0;
	
	DDRD &= 0b11111011;  // configure INT0 as input
	PORTD |= 0b0000100;
	GICR = 1 << INT0;
	MCUCR = (1 << ISC00);
}