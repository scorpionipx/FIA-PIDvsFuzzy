/*
 * eeprom_driver.c
 *
 * Created: 05-Jan-19 19:35:46
 *  Author: ScorpionIPX
 */ 

#include "global.h"
#include "eeprom_driver.h"
#include "fuzzy.h"
#include "pid.h"
#include <string.h>

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
	unsigned int address = FUZY_TABLE_EEPROM_ADDRESS;
	unsigned char byte_l, byte_h;
	for(int i = 0; i < 5; i++)
	{
		for(int j = 0; j < 9; j++)
		{
			byte_l = eeprom_read(address);
			address ++;
			byte_h = eeprom_read(address);
			address ++;
			fuzzy_table[i][j] = (int)((byte_h << 8) + byte_l);
		}
	}
}

void save_fuzzy_table_to_eeprom(void)
{
	unsigned int address = FUZY_TABLE_EEPROM_ADDRESS;
	unsigned char _byte;
	for(int i = 0; i < 5; i++)
	{
		for(int j = 0; j < 9; j++)
		{
			_byte = (unsigned char)(fuzzy_table[i][j]);
			eeprom_write(address, _byte);
			address ++;
			_byte = (unsigned char)(fuzzy_table[i][j] >> 8);
			eeprom_write(address, _byte);
			address ++;
		}
	}
}

void save_pid_constants_to_eeprom(void)
{
	unsigned int address = PID_CONSTANTS_EEPROM_ADDRESS;	unsigned char buffer[4];
	
	memcpy(buffer, &KP, 4);	eeprom_write(address, buffer[0]);	address ++;	eeprom_write(address, buffer[1]);	address ++;	eeprom_write(address, buffer[2]);	address ++;	eeprom_write(address, buffer[3]);	address ++;
	
	memcpy(buffer, &KI, 4);	eeprom_write(address, buffer[0]);	address ++;	eeprom_write(address, buffer[1]);	address ++;	eeprom_write(address, buffer[2]);	address ++;	eeprom_write(address, buffer[3]);	address ++;
	
	memcpy(buffer, &KD, 4);	eeprom_write(address, buffer[0]);	address ++;	eeprom_write(address, buffer[1]);	address ++;	eeprom_write(address, buffer[2]);	address ++;	eeprom_write(address, buffer[3]);	address ++;
}

void load_pid_constants_from_eeprom(void)
{
	unsigned int address = PID_CONSTANTS_EEPROM_ADDRESS;	unsigned char buffer[4];
	
	buffer[0] = eeprom_read(address);
	address ++;
	buffer[1] = eeprom_read(address);
	address ++;
	buffer[2] = eeprom_read(address);
	address ++;
	buffer[3] = eeprom_read(address);
	address ++;
	memcpy(&KP, buffer, 4);
	
	buffer[0] = eeprom_read(address);
	address ++;
	buffer[1] = eeprom_read(address);
	address ++;
	buffer[2] = eeprom_read(address);
	address ++;
	buffer[3] = eeprom_read(address);
	address ++;
	memcpy(&KI, buffer, 4);
	
	buffer[0] = eeprom_read(address);
	address ++;
	buffer[1] = eeprom_read(address);
	address ++;
	buffer[2] = eeprom_read(address);
	address ++;
	buffer[3] = eeprom_read(address);
	address ++;
	memcpy(&KD, buffer, 4);
}