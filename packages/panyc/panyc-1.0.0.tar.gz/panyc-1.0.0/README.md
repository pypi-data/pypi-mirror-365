# Panyc

Super simple python package to solve 2 problems:
- In Python `assert` is not guaranteed to work (see the `-O` flag)
- The very convenient `todo()`/`unreachable()`/... functions to panic in case reached, are missing

### Usage

```python
from panyc import raise_if

def is_even(x):
	raise_if(type(x) != int, f"expected an integer, got {type(x)}")
	return x % 2 == 0

def main():
	x = 6.9
	print("Is", x, "even?", is_even(x))

main()
```
Will result in `AssertionError: /path/to/file/example.py:4: expected an integer, got <class 'float'>`

> A couple of notice:
> - first of all the condition must be true to raise, in the contrary of `assert` where it must be false
> - secondly it raise an `AssertionError` as well, so the error handling remain the same
>
> So if you plan to rewrite your `assert`s you have to change the condition and nothing else


```python
from panyc import todo

def end_world_hungry():
	todo()

def main():
	end_world_hungry()

main()
```
Will result in `NotImplementedError: /path/to/file/example.py:4: Function "end_world_hungry" not implemented`


```python
from panyc import unreachable

def sound(x):
	if x == "cat":
		return "meow"
	elif x == "dog":
		return "woof"
	elif x == "duck":
		return "quack"
	unreachable() # we do not expect other animals

def main():
	print(sound("crocodile"))

main()
```
Will result in `NotImplementedError: /path/to/file/example.py:10: Reached unreachable code in "sound"`

### Installation

Just copy the only file `panyc.py` in your project.

If you like the slop, there's also the package on pypi:
```console
$ pip install panyc
```
