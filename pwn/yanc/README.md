# Y.A.N.C

## Write-up

1. 1st vulnerability:

    - UAF in `edit_note_title` function that lets you edit `victim->bck` where `victim` is the targeted chunk.
    - We use it for **Tcache Stashing Unlink Attack** ([good reference](https://github.com/shellphish/how2heap/blob/master/glibc_2.31/tcache_stashing_unlink_attack.c)).

2. 2nd vulnerability:

    - Negative indexing possible in `clear_note` function.
    - We use it to set the relevant tcache count entry to 0, that way tcache stashing happens, without the need of `calloc`, which isn't used in the program.

3. [Commented exploit script](./solve.py).
