# `fromless`

Create objects that ban unqualified imports.

## Example

In `demo.py`:

```python
from fromless import MustBeQualified   # note the irony

class Qualified(MustBeQualified):
    def __init__(self):
        super().__init__()
```

And at your REPL:

```python
>>> from demo import Qualified
>>> Qualified()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/Users/chrisjrn/src/goodbye_to_from/src/test.py", line 5, in __init__
    super().__init__()
  File "/Users/chrisjrn/src/goodbye_to_from/src/fromless/gtf.py", line 12, in __init__
    MustBeQualified._error_if_unqualified(traceback)
  File "/Users/chrisjrn/src/goodbye_to_from/src/fromless/gtf.py", line 42, in _error_if_unqualified
    raise Exception(f"Class {enclosing_class} was instantiated from an alias.")
Exception: Class Qualified was instantiated from an alias.
>>> import demo
>>> demo.Qualified()
<demo.Qualified object at 0x101509dc0>
```

Perfect.