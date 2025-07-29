# Copyright © 2025 Matteo Benzi <matteo.benzi97@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import inspect

def raise_if(expr, message):
    if expr:
        caller = inspect.stack()[1]
        raise AssertionError(f"{caller.filename}:{caller.lineno}: {message}")

def todo(message=""):
    caller = inspect.stack()[1]
    if len(message) > 0:
        message = f" ({message})"
    raise NotImplementedError(f'{caller.filename}:{caller.lineno}: Function "{caller.function}" not implemented{message}')

def unreachable(message=""):
    caller = inspect.stack()[1]
    if len(message) > 0:
        message = f" ({message})"
    raise NotImplementedError(f'{caller.filename}:{caller.lineno}: Reached unreachable code in "{caller.function}"{message}')
