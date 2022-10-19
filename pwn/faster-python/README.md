# Faster Python

## Write-up

1. We can send negative size when using the `Input` option.

2. That size is converted to an unsigned char in the extension, which means we can actually send a size larger than what the buffer can hold, successfully bypassing the size check in the Python program.

3. We use that buffer overflow for ROP to get a shell, but it's not that easy because we need to leak some stack values first to write them back, else the program would crash.

4. For more details, check out the [commented exploit script](./solve.py).
