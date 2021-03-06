/*
 * usart.c
 *
 * Created: 24-Nov-18 18:34:44
 *  Author: ScorpionIPX
 */ 
#include "global.h"
#include "control_loop.h"
#include "eeprom_driver.h"
#include "display_driver.h"
#include "fuzzy.h"
#include "pid.h"
#include "usart_driver.h"
#include <util/delay.h>
#include <avr/interrupt.h>
#include <string.h> // memcpy

unsigned char expecting_constants;
unsigned char received_constants;
unsigned char received_constants_buffer[90];
unsigned char constant_index;

void init_usart( unsigned int ubrr)
{
	/*Set baud rate */
	UBRRH = (unsigned char)(ubrr>>8);
	UBRRL = (unsigned char)ubrr;
	
	/*Enable receiver and transmitter */
	UCSRB = (1<<RXEN)|(1<<TXEN);
	
	/* Set frame format: 8data, 2stop bit */
	UCSRC = (1<<URSEL)|(1<<USBS)|(3<<UCSZ0);
	expecting_constants = FALSE;
}
void usart_transmit( unsigned char data)
{
	/* Wait for empty transmit buffer */
	while ( !( UCSRA & (1<<UDRE)) )
	;
	/* Put data into buffer, sends the data */
	UDR = data;
}

unsigned char usart_receive(void)
{
	/* Wait for data to be received */
	while ( !(UCSRA & (1<<RXC)) )
	;
	/* Get and return received data from buffer */
	return UDR;
}void transmit_fuzzy_table(void){	int fuzzy_value;	unsigned char fuzzy_value_h;	unsigned char fuzzy_value_l;		for(int i = 0; i < 5; i ++)	{		for(int j = 0; j < 9; j++)		{			fuzzy_value = fuzzy_table[i][j];			fuzzy_value_l = (unsigned char)(fuzzy_value);			fuzzy_value_h = (unsigned char)((fuzzy_value >> 8));						usart_transmit(fuzzy_value_h);			usart_transmit(fuzzy_value_l);		}	}	_delay_ms(1000);}void transmit_pid_constants(void){	unsigned char buffer[4];
	
	memcpy(buffer, &KP, 4);	usart_transmit(buffer[0]);	usart_transmit(buffer[1]);	usart_transmit(buffer[2]);	usart_transmit(buffer[3]);
	
	memcpy(buffer, &KI, 4);	usart_transmit(buffer[0]);	usart_transmit(buffer[1]);	usart_transmit(buffer[2]);	usart_transmit(buffer[3]);
	
	memcpy(buffer, &KD, 4);	usart_transmit(buffer[0]);	usart_transmit(buffer[1]);	usart_transmit(buffer[2]);	usart_transmit(buffer[3]);}void enable_usart_rx_isr(void){
	UCSRB |= (1 << RXCIE); // Enable the USART receive Complete interrupt (USART_RXC)}void disable_usart_rx_isr(void){	UCSRB &= ~(1 << RXCIE); // Disable the USART receive Complete interrupt (USART_RXC)}ISR(USART_RXC_vect)
{
	// Code to be executed when the USART receives a byte here
	unsigned char received_data;
	received_data = UDR; // Fetch the received byte value
	
	if(expecting_constants == EXPECTING_PID_CONSTANTS)
	{
		received_constants_buffer[received_constants] = received_data;
		received_constants ++;
		if(received_constants >= PID_CONSTANTS_TO_RECEIVE)
		{
			expecting_constants = FALSE;
			memcpy(&KP, received_constants_buffer, 4);
			memcpy(&KI, received_constants_buffer + 4, 4);
			memcpy(&KD, received_constants_buffer + 8, 4);
			save_pid_constants_to_eeprom();
			_delay_ms(1);
		}
		return;
	}

	if(expecting_constants == EXPECTING_FUZZY_CONSTANTS)
	{
		received_constants_buffer[received_constants] = received_data;
		received_constants ++;
		if(received_constants >= FUZZY_CONSTANTS_TO_RECEIVE)
		{
			expecting_constants = FALSE;
			for(int i = 0; i < 5; i ++)
			{
				for(int j = 0; j < 9; j ++)
				{
					fuzzy_table[i][j] = (int)((received_constants_buffer[constant_index + 1] << 8) + received_constants_buffer[constant_index]);
					constant_index += 2;
				}
			}
			save_fuzzy_table_to_eeprom();
			_delay_ms(1);
		}
		return;
	}
	
	switch(received_data)
	{
		case 0:
		{
			CONTROL_LOOP = CONTROL_LOOP_NONE;
			OCR1B = 0;
			break;
		}
		case 1:
		{
			if(TARGET_TICKS < MAX_TARGET_TICKS)
			{
				TARGET_TICKS ++;
			}
			break;
		}
		case 2:
		{
			if(TARGET_TICKS > MIN_TARGET_TICKS)
			{
				TARGET_TICKS --;
			}
			break;
		}
		case 3:
		{
			DATA_STREAMING = FALSE;
			disable_usart_rx_isr();
			CONTROL_LOOP = CONTROL_LOOP_NONE;
			OCR1B = 0;
			_delay_ms(3500);
			CONTROL_LOOP = CONTROL_LOOP_PID;
			enable_usart_rx_isr();
			CONTROL_LOOP_START_FLAG = CONTROL_LOOP_START_FLAG_VALUE;
			DATA_STREAMING = TRUE;
			break;
		}
		case 4:
		{
			DATA_STREAMING = FALSE;
			disable_usart_rx_isr();
			CONTROL_LOOP = CONTROL_LOOP_NONE;
			OCR1B = 0;
			_delay_ms(2300);
			CONTROL_LOOP = CONTROL_LOOP_FUZZY;
			enable_usart_rx_isr();
			CONTROL_LOOP_START_FLAG = CONTROL_LOOP_START_FLAG_VALUE;
			DATA_STREAMING = TRUE;
			break;
		}
		case 5:
		{
			if(DATA_STREAMING == TRUE)
			{
				DATA_STREAMING = FALSE;
			}
			else
			{
				DATA_STREAMING = TRUE;
			}
		}
		case 6:
		{
			DATA_STREAMING = FALSE;
			_delay_ms(15);
			expecting_constants = EXPECTING_PID_CONSTANTS;
			received_constants = 0;
			break;
		}
		case 7:
		{
			DATA_STREAMING = FALSE;
			_delay_ms(15);
			expecting_constants = EXPECTING_FUZZY_CONSTANTS;
			received_constants = 0;
			constant_index = 0;
			break;
		}
		case 10:
		{
			transmit_fuzzy_table();
			break;
		}
		case 12:
		{
			transmit_pid_constants();
			break;
		}
	}
}