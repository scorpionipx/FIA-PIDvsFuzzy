/*
 * eeprom_driver.c
 *
 * Created: 05-Jan-19 19:35:46
 *  Author: ScorpionIPX
 */ 

#include "global.h"
#include "eeprom_driver.h"
#include "fuzzy.h"

void eeprom_write(unsigned int address, unsigned char data)
{
	/* Wait for completion of previous write */
	while(EECR & (1 << EEWE));
	/* Set up address and data registers */
	EEAR = address;
	EEDR = data;
	/* Write logical one to EEMWE */
	EECR |= (1 << EEMWE);
	/* Start eeprom write by setting EEWE */
	EECR |= (1 << EEWE);
}

unsigned char eeprom_read(unsigned int address)
{
	/* Wait for completion of previous write */
	while(EECR & (1 << EEWE));
	/* Set up address register */
	EEAR = address;
	/* Start eeprom read by writing EERE */
	EECR |= (1 << EERE);
	/* Return data from data register */
	return EEDR;
}

void load_fuzzy_table_from_eeprom(void)
{
	
}

void save_fuzzy_table_to_eeprom(void)
{
	unsigned int address = FUZY_TABLE_EEPROM_ADDRESS;
	for(int i = 0; i < 5; i++)
	{
		for(int j = 0; j < 9; j++)
		{
			eeprom_write(address, fuzzy_table[i][j]);
			address ++;
		}
	}
}