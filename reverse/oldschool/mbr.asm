	org	0x7C00
	bits	16

start:
	jmp realstart		; Just to look like a more normal MBR
	nop

realstart:
	cli

	xor	ax, ax		; Zero registers for consistency
	mov	ds, ax
	mov	es, ax
	mov	fs, ax
	mov	gs, ax

	mov	ah, 0	; "Teletype output" mode for int 0x10
	mov di, user_input
	mov cx, 8
.cLoop	sub	bl, 1		; Print our message 255 times
	;or	bl, bl
	;jz	doCopy
	;mov	si, user_input
	xor ah, ah
	int 0x16
    stosb			; AL <- [DS:SI] && SI++
    mov ah, 0xe
    int 0x10
	;xor	al, 0x83
	;jz	.sLoop
	loop .cLoop

	xor cx, cx ; i = 0
	mov si, user_input ; buf
	; while (i < 4)
	while_loop:
	cmp cl, 4
	je stop_loop
	mov di, cx
	shl di, 1
	add di, si
	mov ax, [di]
	mov dx, [si+4]
	mov di, [si+6]
	cmp cl, 0
	jne test_1
	mov bx, [si+2]
	jmp loaded_regs
	test_1:
	mov bx, [si]
	cmp cl, 1
	jne test_2
	jmp loaded_regs
	test_2:
	mov dx, [si+2]
	cmp cl, 2
	jne test_3
	jmp loaded_regs
	test_3:
	mov di, [si+4]
	
	loaded_regs:
	rol ax, 8
	rol bx, 8
	rol dx, 8
	rol di, 8
	push ax
	and ax, 0xf0f
	cmp ax, 0xd02
	je x2_test
	cmp ax, 0x700
	je x0_test
	mov ax, ss:[esp]
	and ax, 0xff
	cmp ax, 0x54
	je x1_test
	and ax, 0xf
	cmp al, 2
	je x3_test
	
	x0_test:
	xor bx, dx
	xor bh, 0xf
	and bx, 0xff00
	and di, 0xff00
	cmp bx, di
	jnz set_wrong
	cmp cl, 0
	jnz set_wrong
	jmp continue_test
	x1_test:
	xor bx, dx
	rol bx, 1
	xor bx, 0xf0
	and bx, 0xf0f0
	and di, 0xf0f0
	cmp bx, di
	jnz set_wrong
	cmp cl, 1
	jnz set_wrong
	jmp continue_test
	x2_test:
	xor bx, dx
	xor bx, 0x3536
	cmp bx, di
	jne set_wrong
	cmp cl, 2
	jnz set_wrong
	jmp continue_test
	x3_test:
	xor bx, dx
	and bx, 0xf0f0
	and di, 0xf0f0
	cmp bx, di
	jne set_wrong
	cmp cl, 3
	jnz set_wrong
	jmp continue_test
	set_wrong:
	mov word[right], 0
	continue_test:
	pop ax
	inc cx
	jmp while_loop
stop_loop:
    mov ax, [right]
    test ax, ax
    jnz doCopy
    
    ; wrong
    mov si, wrong
    mov ah, 0xe
    wrong_loop:
    mov al, byte[si]
    xor al, 0x77
    test al, al
    jz stop_printing_wrong
    int 0x10
    inc si
    jmp wrong_loop
    stop_printing_wrong:
    xor ax, ax
    jmp ax
doCopy:
    mov si, correct
    mov ah, 0xe
    correct_loop:
    mov al, byte[si]
    xor al, 0x77
    test al, al
    jz stop_printing_correct
    int 0x10
    inc si
    jmp correct_loop
    stop_printing_correct:
    xor ax, ax
    jmp ax

correct: db 122, 125, 52, 24, 5, 5, 18, 20, 3, 87, 77, 51, 87, 86, 87, 35, 31, 18, 87, 17, 27, 22, 16, 87, 30, 4, 87, 20, 3, 17, 12, 89, 89, 89, 10, 91, 87, 5, 18, 7, 27, 22, 20, 18, 87, 89, 89, 89, 87, 0, 30, 3, 31, 87, 14, 24, 2, 5, 87, 30, 25, 7, 2, 3, 122, 125, 119
wrong: db 122, 125, 32, 5, 24, 25, 16, 87, 77, 80, 95, 87, 86, 87, 35, 5, 14, 87, 22, 16, 22, 30, 25, 122, 125, 119
user_input:	db	0, 0, 0, 0, 0, 0, 0, 0

	align	4		; needed for Disk Address Packet

right:  dw 1

times 510 - ($ - $$) db 0
dw 0xAA55
