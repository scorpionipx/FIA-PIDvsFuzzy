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
	load_fuzzy_table_from_eeprom();
	load_pid_constants_from_eeprom();
	
	_delay_ms(3200);
	enable_usart_rx_isr();
	
	sei();
	
    while (1) 
    {
		display_2d();
    }
}

