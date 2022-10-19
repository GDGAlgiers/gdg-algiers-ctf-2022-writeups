# venomous

## Write-up

1. When importing a Python module, it creates a `__pycache__` directory and puts a bytecode version (`.pyc`) of the module under it and embeds a timestamp that marks the time the module `.py` file was last edited.

2. When you import the module a second time, Python will look for it under `__pycache__` and checks if the timestamp matches with the module file's timestamp, and if it does, it loads that instead of the `.py` file.

3. In this challenge, since the 2 files `main.py` and `echo.py` (the module) are reset every time when running the sudo script, we can instead change the `.pyc` file to change the `print` function call to an `eval` function call (we have to make sure to respect the bytecode format), while also making sure not to modify the embedded timestamp.

4. Now we can run `sudo /challenge/script.sh '__import__("os").system("cat /flag.txt")` to read the flag as `ctf-cracked` user.

5. [Exploit script](./exploit.sh).
