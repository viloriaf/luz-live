#ifndef USB_COMPILE_TIME_VALIDATION_H
#define USB_COMPILE_TIME_VALIDATION_H

/** I N C L U D E S *************************************************/
#include "system\typedefs.h"
#include "system\usb\usb.h"

/** U S B  V A L I D A T I O N **************************************/

#if (EP0_BUFF_SIZE != 8) && (EP0_BUFF_SIZE != 16) && \\
    (EP0_BUFF_SIZE != 32) && (EP0_BUFF_SIZE != 64)
#error(Invalid buffer size for endpoint 0,check "autofiles\usbcfg.h")
#endif

#if defined(HID_INT_OUT_EP_SIZE)
    #if (HID_INT_OUT_EP_SIZE > 64)
        #error(HID Out endpoint size cannot be bigger than 64, check "autofiles\usbcfg.h")
    #endif
#endif

#ifdef HID_INT_IN_EP_SIZE
    #if (HID_INT_IN_EP_SIZE > 64)
        #error(HID In endpoint size cannot be bigger than 64, check "autofiles\usbcfg.h")
    #endif
#endif

#endif //USB_COMPILE_TIME_VALIDATION_H
