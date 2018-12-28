/*
 * fuzzy.h
 *
 * Created: 28-Dec-18 15:17:27
 *  Author: uidq6025
 */ 


#ifndef FUZZY_H_
#define FUZZY_H_

#define FUZZY_ERROR_CLAMPING 30

int fuzzy_error;
int fuzzy_table[5][9];

void init_fuzzy(void);
void fuzzy(void);

#endif /* FUZZY_H_ */