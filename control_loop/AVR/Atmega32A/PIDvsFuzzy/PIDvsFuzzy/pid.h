/*
 * pid.h
 *
 * Created: 24-Nov-18 18:19:01
 *  Author: ScorpionIPX
 */ 


#ifndef PID_H_
#define PID_H_

#define PID_INTEGRAL_MAX_CLAMPING 1500

float KP;
float KI;
float KD;

float pid_error;
float pid_integral;
float pid_derivative;
float pid_previous_error;
float pid_result;

void init_pid(void);
void pid(void);

#endif /* PID_H_ */