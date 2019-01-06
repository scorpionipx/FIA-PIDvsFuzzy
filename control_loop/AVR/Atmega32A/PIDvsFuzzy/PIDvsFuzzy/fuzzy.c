/*
 * fuzzy.c
 *
 * Created: 28-Dec-18 15:17:17
 *  Author: uidq6025
 */ 

#include "global.h"
#include "control_loop.h"
#include "eeprom_driver.h"
#include "fuzzy.h"
#include "optocoupler_driver.h"
#include <util/delay.h>

int fuzzy_error;
int fuzzy_previous_error;
int fuzzy_delta_error;
int fuzzy_result;

int fuzzy_error_index;
int fuzzy_delta_error_index;

int fuzzy_table[5][9] = {
	{-2, -1, 0, 1, 2, 3, 4, 5, 6},
	{-3, -2, -1, 0, 1, 2, 3, 4, 5},
	{-4, -3, -2, -1, 0, 1, 2, 3, 4},
	{-5, -4, -3, -2, -1, 0, 1, 2, 3},
	{-6, -5, -4, -3, -2, -1, 0, 1, 2},
};

void init_fuzzy(void)
{
	fuzzy_error = 0;
	fuzzy_result = 0;
	_delay_ms(1);
	load_fuzzy_table_from_eeprom();
	_delay_ms(1);
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
	
	fuzzy_delta_error = fuzzy_previous_error - fuzzy_error;
	
	fuzzy_error_index = defuzzy_error(fuzzy_error);
	fuzzy_delta_error_index = defuzzy_delta_error(fuzzy_delta_error);
	
	fuzzy_result = fuzzy_table[fuzzy_delta_error_index][fuzzy_error_index];
	
	OCR1B += 2 * fuzzy_result;
	fuzzy_previous_error = fuzzy_error;
}

int defuzzy_error(const int error)
{
	if(error == 0)
	{
		return FUZZY_ERROR_Z;
	}
	if(error <= -23)
	{
		return FUZZY_ERROR_NFM;
	}
	if(error <= -15)
	{
		return FUZZY_ERROR_NM;
	}
	if(error <= -8)
	{
		return FUZZY_ERROR_Nm;
	}
	if(error < 0)
	{
		return FUZZY_ERROR_NFm;
	}
	if(error >= 23)
	{
		return FUZZY_ERROR_PFM;
	}
	if(error >= 15)
	{
		return FUZZY_ERROR_PM;
	}
	if(error >= 8) 
	{
		return FUZZY_ERROR_Pm;
	}
	if(error > 0)
	{
		return FUZZY_ERROR_PFm;
	}
	return 0;
}

int defuzzy_delta_error(const int delta_error)
{
	if(delta_error == 0)
	{
		return FUZZY_DELTA_ERROR_Z;
	}
	if(delta_error <= -15)
	{
		return FUZZY_DELTA_ERROR_NM;
	}
	if(delta_error < 0)
	{
		return FUZZY_DELTA_ERROR_Nm;
	}
	if(delta_error >= 15)
	{
		return FUZZY_DELTA_ERROR_PM;
	}
	if(delta_error > 0)
	{
		return FUZZY_DELTA_ERROR_Pm;
	}
	return 0;
}



