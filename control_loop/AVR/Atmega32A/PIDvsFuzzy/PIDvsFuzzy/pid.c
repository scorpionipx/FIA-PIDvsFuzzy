/*
 * pid.c
 *
 * Created: 24-Nov-18 18:19:10
 *  Author: ScorpionIPX
 */ 

#include "global.h"
#include "pid.h"
#include "control_loop.h"
#include "optocoupler_driver.h"

float KP;
float KI;
float KD;

float pid_error;
float pid_integral;
float pid_derivative;
float pid_previous_error;
float pid_result;

void init_pid(void)
{
	KP = 50;
	KI = 1.2;
	KD = 10;

	pid_error = 0;
	pid_integral = 0;
	pid_derivative = 0;
	pid_previous_error = 0;
	pid_result = 0;
}

void pid(void)
{
	pid_error = TARGET_TICKS - TICKS;
	if(pid_error == 0)
	{
		return;
	}
	pid_integral += pid_error;
	if(pid_integral > PID_INTEGRAL_MAX_CLAMPING)  // pid loop integral clamping
	{
		pid_integral = PID_INTEGRAL_MAX_CLAMPING;
	}
	pid_derivative = pid_previous_error - pid_error;
	pid_result = (KP * pid_error) + (KI * pid_integral) + (KD * pid_derivative);
	if(pid_result < 0)
	{
		pid_result = 0;
	}
	
	OCR1B = (unsigned int) (pid_result);
	
	if(OCR1B > ICR1)
	{
		OCR1B = ICR1;
	}
	pid_previous_error = pid_error;
}


