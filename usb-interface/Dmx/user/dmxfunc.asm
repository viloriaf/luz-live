	include "p18F2550.inc"

	udata
coun 	res 1
	extern	dmx_byte
	extern	ProcessUSBData
	code

	global send_init_trame
	global send_byte


send_init_trame
		bcf		PORTC,0	; Debut BREAK Bit 1
		call	Delay
		call	DelaySup
		bcf		PORTC,0	; BREAK Bit 2
		call	Delay	
		call	DelaySup
		bcf		PORTC,0	; BREAK Bit 3
		call	Delay
		call	DelaySup
		bcf		PORTC,0	; BREAK Bit 4
		call	Delay
		call	DelaySup
		bcf		PORTC,0	; BREAK Bit 5
		call	Delay
		call	DelaySup
		bcf		PORTC,0	; BREAK Bit 6
		call	Delay
		call	DelaySup
		bcf		PORTC,0	; BREAK Bit 7
		call	Delay
		call	DelaySup
		bcf		PORTC,0	; BREAK Bit 8
		call	Delay
		call	DelaySup
		bcf		PORTC,0	; BREAK Bit 9
		call	Delay
		call	DelaySup
		bcf		PORTC,0	; BREAK Bit 10
		call	Delay
		call	DelaySup
		bcf		PORTC,0	; BREAK Bit 11
		call	Delay
		call	DelaySup
		bcf		PORTC,0	; BREAK Bit 12
		call	Delay
		call	DelaySup	
		bcf		PORTC,0	; BREAK Bit 13
		call	Delay
		call	DelaySup
		bcf		PORTC,0	; BREAK Bit 14
		call	Delay
		call	DelaySup
		bcf		PORTC,0	; BREAK Bit 15
		call	Delay
		call	DelaySup
		bcf		PORTC,0	; BREAK Bit 16
		call	Delay
		call	DelaySup
		bcf		PORTC,0	; BREAK Bit 17
		call	Delay
		call	DelaySup
		bcf		PORTC,0	; BREAK Bit 18
		call	Delay
		call	DelaySup
		bcf		PORTC,0	; BREAK Bit 19
		call	Delay
		call	DelaySup
		bcf		PORTC,0	; BREAK Bit 20
		call	Delay
		call	DelaySup
		bcf		PORTC,0	; BREAK Bit 21
		call	Delay
		call	DelaySup
		bcf		PORTC,0	; BREAK Bit 22
		call	Delay
		call	DelaySup
		bsf		PORTC,0	; MAB Bit 1
		call	Delay
		call	DelaySup
		bsf		PORTC,0	; MAB Bit 2
		call	Delay

		return


send_byte
			bcf		PORTC,0	;	Start BIT
			nop
			nop

Bit0:		call 	Delay		; 	BIT 0
			btfsc	dmx_byte,0
			bra		SetBit0
			bra		ClearBit0

SetBit0:	nop
			bsf		PORTC,0
			bra		Bit1

ClearBit0:	bcf		PORTC,0
			bra		Bit1

Bit1:		call 	Delay		; 	BIT 1
			btfsc	dmx_byte,1
			bra		SetBit1
			bra		ClearBit1

SetBit1:	nop
			bsf		PORTC,0
			bra		Bit2

ClearBit1:	bcf		PORTC,0
			bra		Bit2


Bit2:	;;	call changeLed ;;
			call 	Delay		; 	BIT 2
			btfsc	dmx_byte,2
			bra		SetBit2
			bra		ClearBit2

SetBit2:	nop
			bsf		PORTC,0
			bra		Bit3

ClearBit2:	bcf		PORTC,0
			bra		Bit3

Bit3:	;;	call changeLed ;;
			call 	Delay		; 	BIT 3
			btfsc	dmx_byte,3
			bra		SetBit3
			bra		ClearBit3

SetBit3:	nop
			bsf		PORTC,0
			bra		Bit4

ClearBit3:	bcf		PORTC,0
			bra		Bit4

Bit4:		call 	Delay,0		; 	BIT 4
			btfsc	dmx_byte,4
			bra		SetBit4
			bra		ClearBit4

SetBit4:	nop
			bsf		PORTC,0
			bra		Bit5

ClearBit4:	bcf		PORTC,0
			bra		Bit5

Bit5:		call 	Delay,0		; 	BIT 5
			btfsc	dmx_byte,5
			bra		SetBit5
			bra		ClearBit5

SetBit5:	nop
			bsf		PORTC,0
			bra		Bit6

ClearBit5:	bcf		PORTC,0
			bra		Bit6

Bit6:		call 	Delay		; 	BIT 6
			btfsc	dmx_byte,6
			bra		SetBit6
			bra		ClearBit6

SetBit6:	nop
			bsf		PORTC,0
			bra		Bit7

ClearBit6:	bcf		PORTC,0
			bra		Bit7

Bit7:		call 	Delay		; 	BIT 7
			btfsc	dmx_byte,7
			bra		SetBit7
			bra		ClearBit7

SetBit7:	nop
			bsf		PORTC,0
			bra		StopBit

ClearBit7:	bcf		PORTC,0
			bra		StopBit

StopBit:	call	Delay
			nop
			nop
			nop
			nop
			bsf		PORTC,0	;	STOP bit #1
			call	Delay
			call	DelaySup
			bsf		PORTC,0	;	STOP bit #2
			call	Delay
			call	DelaySup
			return



Delay:		movlw	0x0C	
			movwf	coun
Count:		decfsz	coun,f
			bra		Count
			return


DelaySup:	nop
			nop
			return

	end