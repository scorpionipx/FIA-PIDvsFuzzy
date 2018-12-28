/*
 * adc_driver.h
 *
 * Created: 04-Dec-18 22:43:42
 *  Author: ScorpionIPX
 */ 


#ifndef ADC_DRIVER_H_
#define ADC_DRIVER_H_

#define POWER_SUPPLY_VOLTAGE_ADC_CHANNEL 0

void init_adc(void);
uint16_t adc_get_value(uint8_t ch);

#endif /* ADC_DRIVER_H_ */