/*
 * display.h
 *
 * Created: 24-Nov-18 17:23:56
 *  Author: ScorpionIPX
 */ 


#ifndef DISPLAY_H_
#define DISPLAY_H_

#define MULTIPLEX_DELAY_MS 1

#define DIGIT_0 0b10000001
#define DIGIT_1 0b11110011
#define DIGIT_2 0b01001001
#define DIGIT_3 0b01100001
#define DIGIT_4 0b00110011
#define DIGIT_5 0b00100101
#define DIGIT_6 0b00000101
#define DIGIT_7 0b11110001
#define DIGIT_8 0b00000001
#define DIGIT_9 0b00100001

uint8_t DIGIT[10];
uint8_t DISPLAY_BUFFER[4];

void init_display();

void display_2d();
void display_4d();
void update_display_buffer_2d(const unsigned int number);
void update_display_buffer_4d(const unsigned int number);


#endif /* DISPLAY_H_ */