/*
 * control_loop.c
 *
 * Created: 28-Dec-18 15:22:13
 *  Author: uidq6025
 */ 

#include "global.h"
#include <avr/interrupt.h>
#include "adc_driver.h"
#include "control_loop.h"
#include "display_driver.h"
#include "fuzzy.h"
#include "optocoupler_driver.h"
#include "pid.h"
#include "usart_driver.h"

int TARGET_TICKS;
unsigned char start_flag_counter = 5;

void init_control_loop(void)
{
	// set up timer with prescaler = 1024
	TCCR0 |= (1 << CS02)|(1 << CS00);
	
	// initialize counter
	TCNT0 = 0;
	
	// enable overflow interrupt
	TIMSK |= (1 << TOIE0);
	DATA_STREAMING = FALSE;
	REVOLUTIONS_PER_MINUTE = 0;
	TICKS = 0;
	TARGET_TICKS = 0;
	CONTROL_LOOP_START_FLAG = 0;
	// CONTROL_LOOP = CONTROL_LOOP_PID;
	CONTROL_LOOP = CONTROL_LOOP_NONE;
}

ISR(INT0_vect)  // external interrupt_zero ISR (INT0)
{
	INT0_CNT++;
	TICKS ++;
	if(INT0_CNT >= TICKS_PER_REVOLUTION)
	{
		REVOLUTIONS ++;
	}
}

// interrupt routine running every 16.384 ms
ISR(TIMER0_OVF_vect)
{
	TIMER0_CNT ++;
	
	switch(CONTROL_LOOP)
	{
		case CONTROL_LOOP_PID:
		{
			pid();
			break;
		}
		case CONTROL_LOOP_FUZZY:
		{
			fuzzy();
			break;
		}
		default:
		{
			break;
		}
	}
	
	power_supply_voltage = adc_get_value(POWER_SUPPLY_VOLTAGE_ADC_CHANNEL);
	power_supply_voltage >>= 2;  // 8 bit compatible
	
	if(TIMER0_CNT >= 10)  // update display info every 163.84 ms
	{
		 update_display_buffer_2d(TICKS);
		TIMER0_CNT = 0;
	}
	if(DATA_STREAMING)
	{
		usart_transmit(255);
		usart_transmit(TARGET_TICKS);
		usart_transmit(TICKS);
		usart_transmit((uint8_t)(power_supply_voltage));
		usart_transmit(CONTROL_LOOP);
		usart_transmit(CONTROL_LOOP_START_FLAG);
	}
	TICKS = 0;
	if(CONTROL_LOOP_START_FLAG)
	{
		start_flag_counter --;
		if(start_flag_counter == 0)
		{
			start_flag_counter = CONTROL_LOOP_START_FLAG_LENGTH;
			CONTROL_LOOP_START_FLAG = 0;
		}
	}
}
