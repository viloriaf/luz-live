/** I N C L U D E S **********************************************************/
#include <p18cxxx.h>
#include "system\typedefs.h"

#include "system\usb\usb.h"

#include "io_cfg.h"             // I/O pin mapping
#include "user\user.h"
#include <delays.h>
/** V A R I A B L E S ********************************************************/
#pragma udata
unsigned char i;
unsigned char input_enable,max_chan;
unsigned char dmx_byte,send_count;
unsigned char start,stop,data_ready;
unsigned char input_buffer[64];
unsigned char dmx[64];

unsigned char isrcount, ledflag;

#pragma code
/** P R I V A T E  P R O T O T Y P E S ***************************************/
void ProcessUSBData(void);
void SendDMXTrame();
extern void send_init_trame(void);
extern void send_byte(void);
void InterruptHandler (void);
#pragma code

/** I N T E R R U P T S ***************************************/
#pragma interruptlow InterruptHandler
void InterruptHandler (void)
{
	if (PIR1bits.TMR2IF==1)
	{
		PIR1bits.TMR2IF=0; // clear interrupt flag
		if (isrcount<4)
			isrcount++;
		else {
			isrcount=0;
			ledflag=1;
			T2CONbits.TMR2ON=0;
			TMR2=0;
		}
	}
}

/** D E C L A R A T I O N S **************************************************/
#pragma code
//----------------------------------
// Initialization function
//--------------------------------------------
void UserInit(void)
{
	for (i=0;i<64;i++)
		dmx[i]=0;

	RCONbits.IPEN=1; 	// enable interrupt priority
	PIR1=0;				// clear peripheral interrupt flags
	PIE1bits.TMR2IE=1;	// enable timer interrupt
	IPR1bits.TMR2IP=0;	// low priority interrupt
	T2CON=0b01111011;	// timer 2 : post 8 pre 16
	INTCONbits.GIEH=1;	// enable high interrupt
	INTCONbits.GIEL=1;	// enable low interrupt
	
	isrcount=0;
	ledflag=0;

	mInitAllLEDs();
	mInitSwitch();
    
	TRISB=0xFF;
	input_enable=0;
	max_chan=0x40;
	send_count = 0;
	TMR2=0;
	T2CONbits.TMR2ON=1;
}//end UserInit

//----------------------------------
// ProcessIO function
//--------------------------------------------
void ProcessIO(void)
{   
	/*send_count ++;
	if (send_count>20)
	{
		SendDMXTrame();
		send_count=0;
	}*/

	if (ledflag==1)
	{
		ledflag=0;
		LED_1_Toggle();
		//SendDMXTrame();
		T2CONbits.TMR2ON=1;
	}
	if((usb_device_state < CONFIGURED_STATE)) return;
    ProcessUSBData();
    
}//end ProcessIO

//----------------------------------
// Trame sending function
//----------------------------------
void SendDMXTrame(void)
{
	send_init_trame();
	dmx_byte=0x00;
	send_byte();
	for (i=0 ; i<max_chan ; i++)
	{
		dmx_byte=dmx[i];
		send_byte();
	}
}
//----------------------------------
// DMX input capture
//----------------------------------


//----------------------------------
// USB input/ouput management
//--------------------------------------------
void ProcessUSBData(void)
{
	if (HIDRxReport(input_buffer,64))
	{
		
		data_ready=1;
		switch(input_buffer[0])
		{
			case update_DMX:
				LED_2_Toggle();
				start=input_buffer[1];
				stop=input_buffer[1]+input_buffer[2];
				if (stop>255) stop=255;
				for (i=start;i<stop;i++)
					dmx[i]=input_buffer[i-start+3];
				break;
			case config_OUTPUT:
				max_chan=input_buffer[1];
				break;
			case config_INPUT:
				input_enable=(input_buffer[1]==1);
				break;
			default:
				break;
		}
	}

    if (data_ready && input_enable && !mHIDTxIsBusy())
    {
        HIDTxReport(dmx,64);
		data_ready=0;
    }

}//end Process_Data


/** EOF user.c *********************************************************/
