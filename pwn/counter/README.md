# Counter

## Write-up

1. Variable `counter` of type `unsigned char` is initialized to `1`.

2. We can increment `counter`, and decrement it if it's strictly greater than `1`.

3. To print the flag, the goal is to set `counter` to `0`.

4. Since the size of `unsigned char` is only one byte, i.e. values are in range `0-255`, we can increment `counter` 255 times and its value will wrap up back to `0`.

5. Run [exploit script](./solve.py).
