/*
 * display.c
 *
 * Created: 24-Nov-18 17:23:47
 *  Author: ScorpionIPX
 */ 

#include "global.h"
#include "display_driver.h"
#include <util/delay.h>

uint8_t DIGIT[10] = {DIGIT_0, DIGIT_1, DIGIT_2, DIGIT_3, DIGIT_4, DIGIT_5, DIGIT_6, DIGIT_7, DIGIT_8, DIGIT_9};
uint8_t DISPLAY_BUFFER[4] = {0};
	
void init_display()
{
	DDRB |= 0x0F;
	PORTB &= 0xF0;
	DDRC = 0xFF;
	PORTC = 0x00;
}
	
void update_display_buffer_4d(const unsigned int number)
{
	unsigned int _number = number;
	DISPLAY_BUFFER[0] = DIGIT[_number % 10];
	_number /= 10;
	DISPLAY_BUFFER[1] = DIGIT[_number % 10];
	_number /= 10;
	DISPLAY_BUFFER[2] = DIGIT[_number % 10];
	_number /= 10;
	DISPLAY_BUFFER[3] = DIGIT[_number % 10];
}	

	
void update_display_buffer_2d(const unsigned int number)
{
	unsigned int _number = number;
	DISPLAY_BUFFER[0] = DIGIT[_number % 10];
	_number /= 10;
	DISPLAY_BUFFER[1] = DIGIT[_number % 10];
}

void display_4d()
{
	PORTB |= 0b00001111;
	PORTB &= 0b11111110;
	PORTC = DISPLAY_BUFFER[3];
	_delay_ms(MULTIPLEX_DELAY_MS);
	PORTB |= 0b00001111;
	PORTB &= 0b11111101;
	PORTC = DISPLAY_BUFFER[2];
	_delay_ms(MULTIPLEX_DELAY_MS);
	PORTB |= 0b00001111;
	PORTB &= 0b11111011;
	PORTC = DISPLAY_BUFFER[1];
	_delay_ms(MULTIPLEX_DELAY_MS);
	PORTB |= 0b00001111;
	PORTB &= 0b11110111;
	PORTC = DISPLAY_BUFFER[0];
	_delay_ms(MULTIPLEX_DELAY_MS);
	PORTC = 0xFF;
}

void display_2d()
{
	PORTB |= 0b00001111;
	PORTB &= 0b11111011;
	PORTC = DISPLAY_BUFFER[1];
	_delay_ms(MULTIPLEX_DELAY_MS);
	PORTB |= 0b00001111;
	PORTB &= 0b11110111;
	PORTC = DISPLAY_BUFFER[0];
	_delay_ms(MULTIPLEX_DELAY_MS);
	PORTC = 0xFF;
}