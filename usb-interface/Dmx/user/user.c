/** I N C L U D E S **********************************************************/
#include <p18cxxx.h>
#include "system\typedefs.h"
#include "system\usb\usb.h"
#include "io_cfg.h"             // I/O pin mapping
#include "user\user.h"

/** V A R I A B L E S ********************************************************/
#pragma udata
unsigned char i;
unsigned char input_enable,max_chan;
unsigned char dmx_byte,send_count;
unsigned char start,stop,data_ready;
unsigned char input_buffer[64];
unsigned char dmx[64];

unsigned char isrflag;

#pragma code
/** P R I V A T E  P R O T O T Y P E S ***************************************/
void ProcessUSBData(void);
void SendDMXTrame();
extern void send_init_trame(void);
extern void send_byte(void);
#pragma code

/** I N T E R R U P T S ***************************************/
#pragma interruptlow timer_isr
void timer_isr (void)
{
	if (INTCONbits.TMR0IF==1)
	{
		INTCONbits.TMR0IF = 0; // clear interrupt flag
		T0CONbits.TMR0ON=0;
		TMR0L=TMR0H=0;
		isrflag=1;
	}
}

/** D E C L A R A T I O N S **************************************************/
#pragma code
//----------------------------------
// Initialization function
//--------------------------------------------
void UserInit(void)
{
	mInitAllLEDs();
	mInitDMX();
	mInitSwitch();

	for (i=0;i<64;i++)
		dmx[i]=0x00;
	
	T0CON = 0b0000001;
	TMR0L = TMR0H = 0;
	INTCONbits.T0IF = 0;
	INTCONbits.T0IE = 1;
	INTCONbits.GIE = 0;
	T0CONbits.TMR0ON = 1;

	//TRISC = 0b00000110;
	//LATC = 0;

	isrflag = 0;
	input_enable=0;
	max_chan=0x40;
}//end UserInit

//----------------------------------
// ProcessIO function
//--------------------------------------------
void ProcessIO(void)
{
	INTCONbits.GIE=1;
	if (isrflag)
	{
		isrflag=0;
		SendDMXTrame();
		LED_1_Toggle()
		T0CONbits.TMR0ON = 1;	
	}
	INTCONbits.GIE=0;

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
// USB input/ouput management
//--------------------------------------------
void ProcessUSBData(void)
{
	if (HIDRxReport(input_buffer,64))
	{
		data_ready=1;
		LED_2_Toggle()
		switch(input_buffer[0])
		{
			case update_DMX:
				start=input_buffer[1];
				stop=input_buffer[1]+input_buffer[2];
				if (stop>255) stop=255;
				for (i=start;i<stop;i++)
					dmx[i]=input_buffer[i-start+3];
				//dmxO = LED_1 = input_buffer[3];
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
