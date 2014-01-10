# -*- coding: utf-8 -*-
"""
Contexter is a full replacement of the :module:`contextlib` standard library
module. It comes with more features, a nicer API and full support for
Python 2.5 up to 3.x from a single source file.
"""

__author__ = 'Marcel Hellkamp'
__version__ = '0.1'
__license__ = 'MIT'

import sys
from contextlib import contextmanager
from functools import wraps

__all__ = ['Contexter']
__all__ += ['contextmanager', 'nested', 'closing', 'ContextDecorator',
            'ExitStack']


_not_a_context = TypeError(
    "Only context managers (implementing `__enter__` and `__exit__`)"
    " or objects with a `close` method are supported.")


class Contexter(object):
    __slots__ = '_prepared', '_context_stack'

    def __init__(self, *contexts):
        self._prepared = list(contexts)
        self._context_stack = []

    def __call__(self, *contexts):
        for context in contexts:
            self << context
        return self

    def values(self, stack=-1):
        return [value for context, value in self._context_stack[stack]]

    def value(self, index, stack=-1):
        return self._context_stack[stack][i][1]

    __getitem__ = value

    def __len__(self):
        return len(self._context_stack[-1])

    def append(self, context):
        if hasattr(context, '__enter__') and hasattr(context, '__exit__'):
            value = context.__enter__()
            self._context_stack[-1].append((context, value))
            return value
        elif hasattr(context, 'close'):
            self._context_stack[-1].append((context, context))
            return context
        else:
            raise _not_a_context

    __lshift__ = append

    def __enter__(self):
        self._context_stack.append([])
        if self._context_stack == [[]]:
            for context in self._prepared:
                self << context
        return self

    def __exit__(self, *exc):
        contexts = self._context_stack.pop()
        for context, value in contexts[::-1]:
            try:
                if hasattr(context, '__exit__'):
                    if(context.__exit__(*exc)):
                        exc = (None, None, None)
                elif hasattr(context, 'close'):
                    context.close()
                else:
                    raise _not_a_context
            except:
                exc = sys.exc_info()

        self._active = False
        if exc != (None, None, None):
            raise exc[0], exc[1], exc[2]

    def close(self):
        self.__exit__(None, None, None)


class _ExitDummy(object):
    def __init__(self, exit):
        self.exit = exit

    def __enter__(self):
        return self

    def __exit__(self, *ext):
        return self.exit(*exc)


class _CloseDummy(object):
    def __init__(self, callback, args, kwds):
        self.callback = callback
        self.args = args
        self.kwds = kwds

    def __call__(self, *args, **kwds):
        return self.callback(*args, **kwds)

    def close(self):
        self.callback(*self.args, **self.kwds)


class ExitStack(Contexter):
    """ Context manager for dynamic management of a stack of exit callbacks.
    """

    def enter_context(self, cm):
        """ Enters the supplied context manager

            If successful, also pushes its __exit__ method as a callback and
            returns the result of the __enter__ method.
        """
        return self << cm

    def push(self, exit):
        """ Registers a callback with the standard __exit__ method signature

            Can suppress exceptions the same way __exit__ methods can.

            Also accepts any object with an __exit__ method (registering a call
            to the method instead of the object itself)
        """
        return self << _ExitDummy(exit)

    def callback(self, callback, *args, **kwds):
        """ Registers an arbitrary callback and arguments.

            Cannot suppress exceptions.
        """
        return self << _CloseDummy(callback, args, kwds)

    def pop_all(self):
        """ Preserve the context stack by transferring it to a new instance """
        ret = ExitStack()
        ret._context_stack.append(self._context_stack.pop())
        self._context_stack.append([])


def closing(thing):
    return Contexter(thing)


def nested(*args):
    return Contexter(*args)


class ContextDecorator(object):
    """ A base class or mixin that enables context managers to work as
        decorators. """
    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwds):
            with self:
                return func(*args, **kwds)
        return inner









def test_context_stacks():

    class TestContext(object):
        def __init__(self, name):
            self.name = name
            self.entered = False
            self.exited = False

        def __enter__(self):
            print 'entering', self.name
            self.entered = True
            return self.name

        def __exit__(self, *a):
            self.exited = a
            print 'exiting', self.name, a

    with Contexter(TestContext('a')) as ctx:
        assert ctx.values() == ['a']
        v1 = ctx.append(TestContext('b'))
        assert ctx.values() == ['a','b']
        assert v1 == 'b'
        v2 = ctx << TestContext('c')
        assert ctx.values() == ['a','b','c']
        assert v2 == 'c'



