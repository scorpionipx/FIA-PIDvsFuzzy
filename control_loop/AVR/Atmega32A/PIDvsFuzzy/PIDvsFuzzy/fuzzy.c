/*
 * fuzzy.c
 *
 * Created: 28-Dec-18 15:17:17
 *  Author: uidq6025
 */ 

#include "global.h"
#include "control_loop.h"
#include "fuzzy.h"
#include "optocoupler_driver.h"

int fuzzy_error;

int fuzzy_table[5][9] = {
	{0, 0, 0, 0, 0, 0, 0, 0, 0},
	{0, 0, 0, 0, 0, 0, 0, 0, 0},
	{0, 0, 0, 0, 0, 0, 0, 0, 0},
	{0, 0, 0, 0, 0, 0, 0, 0, 0},
	{0, 0, 0, 0, 0, 0, 0, 0, 0},
};

void init_fuzzy(void)
{
	fuzzy_error = 0;
}

void fuzzy(void)
{
	fuzzy_error = TARGET_TICKS - TICKS;
	if(fuzzy_error < -FUZZY_ERROR_CLAMPING)  // error clamping
	{
		fuzzy_error = -FUZZY_ERROR_CLAMPING;
	}
	if(fuzzy_error > FUZZY_ERROR_CLAMPING)
	{
		fuzzy_error = FUZZY_ERROR_CLAMPING;
	}
	OCR1B += 0;
	
}