#ifndef USER_H
#define USER_H

/** D E F I N I T I O N S *****************/

#define	update_DMX	0
#define config_OUTPUT	1
#define config_INPUT	2

/** P U B L I C  P R O T O T Y P E S ******************/
void UserInit(void);
void ProcessIO(void);
void InterruptHandler(void);
#endif //USER_H
