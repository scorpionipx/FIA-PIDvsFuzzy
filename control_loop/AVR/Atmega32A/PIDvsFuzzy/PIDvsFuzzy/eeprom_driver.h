/*
 * eeprom_driver.h
 *
 * Created: 05-Jan-19 19:40:51
 *  Author: ScorpionIPX
 */ 


#ifndef EEPROM_DRIVER_H_
#define EEPROM_DRIVER_H_

#define FUZY_TABLE_EEPROM_ADDRESS 0x20  // range: [0x20 (32), 4D(77)]

void eeprom_write(unsigned int address, unsigned char data);
unsigned char eeprom_read(unsigned int address);

void load_fuzzy_table_from_eeprom(void);
void save_fuzzy_table_to_eeprom(void);

#endif /* EEPROM_DRIVER_H_ */