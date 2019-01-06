/*
 * PIDvsFuzzy.c
 *
 * Created: 28-Dec-18 15:05:26
 * Author : uidq6025
 */ 

#include "global.h"

#include <util/delay.h>
#include <avr/interrupt.h>

#include "adc_driver.h"
#include "control_loop.h"
#include "display_driver.h"
#include "eeprom_driver.h"
#include "fuzzy.h"
#include "optocoupler_driver.h"
#include "pid.h"
#include "pwm_driver.h"
#include "usart_driver.h"


int main(void)
{
	_delay_ms(100);
	init_adc();
	init_control_loop();
	init_display();
	init_fuzzy();
	init_optocoupler();
    init_pid();
	init_pwm();
	init_usart(MYUBRR);
	
	_delay_ms(200);
	UCSRB |= (1 << RXCIE); // Enable the USART receive Complete interrupt (USART_RXC)
	
	sei();
	
    while (1) 
    {
		display_2d();
    }
}

