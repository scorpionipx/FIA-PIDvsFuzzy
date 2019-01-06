/*
 * usart.c
 *
 * Created: 24-Nov-18 18:34:44
 *  Author: ScorpionIPX
 */ 
#include "global.h"
#include "display_driver.h"
#include "fuzzy.h"
#include "pid.h"
#include "usart_driver.h"
#include <util/delay.h>
#include <avr/interrupt.h>
#include <string.h> // memcpy

void init_usart( unsigned int ubrr)
{
	/*Set baud rate */
	UBRRH = (unsigned char)(ubrr>>8);
	UBRRL = (unsigned char)ubrr;
	
	/*Enable receiver and transmitter */
	UCSRB = (1<<RXEN)|(1<<TXEN);
	
	/* Set frame format: 8data, 2stop bit */
	UCSRC = (1<<URSEL)|(1<<USBS)|(3<<UCSZ0);
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
	
	memcpy(buffer, &KP, 4 );	usart_transmit(buffer[0]);	usart_transmit(buffer[1]);	usart_transmit(buffer[2]);	usart_transmit(buffer[3]);
	
	memcpy(buffer, &KI, 4 );	usart_transmit(buffer[0]);	usart_transmit(buffer[1]);	usart_transmit(buffer[2]);	usart_transmit(buffer[3]);
	
	memcpy(buffer, &KD, 4 );	usart_transmit(buffer[0]);	usart_transmit(buffer[1]);	usart_transmit(buffer[2]);	usart_transmit(buffer[3]);}ISR(USART_RXC_vect)
{
	// Code to be executed when the USART receives a byte here
	unsigned char received_data;
	received_data = UDR; // Fetch the received byte value
	if(received_data)
	{
		update_display_buffer_2d(received_data);
	}
	switch(received_data)
	{
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