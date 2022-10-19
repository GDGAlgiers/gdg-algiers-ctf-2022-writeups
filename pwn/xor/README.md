# XOR

## Write-up

1. Vulnerable piece of code:

    ```c
    void input_size(unsigned long *size, unsigned long maxsize) {
        char answer;

        while (answer != 'y') {
            *size = get_num("Enter XOR buffer size: ");
            printf("Entered size: %lu\n", *size);
            if (*size < 1 || *size > maxsize) {
                error("Wrong size");
            } else {
                printf("Done? [y/n] ");
                answer = getchar();
                while ((getchar()) != '\n');
            }
        }

        return;
    }
    ```

2. Variable `answer` is not initialized, it takes whatever value there was on its allocated stack space.

3. Since the `greet()` function was called before `input_size()` (before `main()`), and the stack frame was pretty big to account for the `name` variable, the `answer` variable will take a value off of a specific offset from `name`.

4. If we manage to make that value the char `'y'`, it will never enter the while loop, consequently, the `size` variable will stay uninitialized (because it's uninitialized in `menu()`).

5. Combining that with the fact that we can also control the value of `size` using the `name` variable (just like the `answer` variable), we can set an arbitrary read/write size for the `buf` variable in `menu()` (stack information leak and stack buffer overflow).

6. We use the information leak to leak the canary and a libc address.

7. We use the buffer overflow for ROP to shell.

8. [Commented exploit script](./solve.py).
