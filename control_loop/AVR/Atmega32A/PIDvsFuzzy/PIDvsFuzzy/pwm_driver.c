/*
 * pwm.c
 *
 * Created: 24-Nov-18 18:57:58
 *  Author: ScorpionIPX
 */ 

#include "global.h"

void init_pwm(void)
{
	DDRD |= 0b00110000;
	ICR1 = 1200; /*CUSTOM TOP OF TIMER1*/
	TCCR1A = 0b10100010; /*SET PWM ON BOTH PD4 AND PD5*/
	TCCR1B = 0b00011001; /*0x19*/
	OCR1A = 0; /*FACTOR DE UMPLERE PWM1: 0:ICR1*/
	OCR1B = 0; /*FACTOR DE UMPLERE PWM2: 0:ICR1*/
}