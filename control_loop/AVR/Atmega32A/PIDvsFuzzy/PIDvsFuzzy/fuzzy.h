/*
 * fuzzy.h
 *
 * Created: 28-Dec-18 15:17:27
 *  Author: uidq6025
 */ 


#ifndef FUZZY_H_
#define FUZZY_H_

#define FUZZY_ERROR_CLAMPING 30

#define FUZZY_ERROR_NFM 0
#define FUZZY_ERROR_NM 1
#define FUZZY_ERROR_Nm 2
#define FUZZY_ERROR_NFm 3
#define FUZZY_ERROR_Z 4
#define FUZZY_ERROR_PFm 5
#define FUZZY_ERROR_Pm 6
#define FUZZY_ERROR_PM 7
#define FUZZY_ERROR_PFM 8

#define FUZZY_DELTA_ERROR_NM 0
#define FUZZY_DELTA_ERROR_Nm 1
#define FUZZY_DELTA_ERROR_Z 2
#define FUZZY_DELTA_ERROR_Pm 3
#define FUZZY_DELTA_ERROR_PM 4

int fuzzy_error;
int fuzzy_table[5][9];

void init_fuzzy(void);
void fuzzy(void);

int defuzzy_error(const int error);
int defuzzy_delta_error(const int delta_error);

#endif /* FUZZY_H_ */