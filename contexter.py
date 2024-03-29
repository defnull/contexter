# -*- coding: utf-8 -*-
"""
Contexter is a full replacement of the contextlib standard library
module. It comes with more features, a nicer API and full support for
Python 2.5 up to 3.x from a single source file.
"""

__author__ = 'Marcel Hellkamp'
__version__ = '0.1.4'
__license__ = 'MIT'

import sys
import contextlib
import functools
import warnings

__all__ = ['Contexter']
__all__ += ['contextmanager', 'nested', 'closing', 'ContextDecorator',
            'ExitStack']



if sys.version_info < (3,):
	eval(compile('def reraise(a): raise a[0], a[1], a[2]', '<py3fix>', 'exec'))
else:
    def reraise(exc):
        raise exc[1].with_traceback(exc[2])



_not_a_context = TypeError(
    "Only context managers (implementing `__enter__` and `__exit__`)"
    " or objects with a `close` method are supported.")


class Contexter(object):
    """ A context-manager manager, designed to make it easy to programmatically
        combine other context managers and cleanup functions. Additional
        contexts can be added afte-the-fact and are still cleanded-up as if they
        were part of the original `with` statement.

        The same context manager can be used in a nested `with` statement and
        behaves as if a new instance was used: At the end of a nested `with`
        statement, only the contexts from the inner scope are closed.

        Closeable objects (implement `close()`) can be added directly, without
        a `contextlib.closing` wrapper.
    """
    __slots__ = '_prepared', '_context_stack'

    def __init__(self, *contexts):
        """ Create a new context manager with any number of child contexts. """
        self._prepared = list(contexts)
        self._context_stack = []

    def __call__(self, *contexts):
        """ Add any number of additional contexts to the current scope. """
        for context in contexts:
            self << context
        return self

    def append(self, context):
        """ Add a new child context to the current scope.

            @param context: Either a context manager implemeting `__enter__` and
                `__exit__`, or a closeable object.
            @return The return value of `__enter__()`, or the closeable itself.
        """
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

    def values(self, stack=-1):
        """ Return all context values as a list.

            Return a list of context values (the value returned by
            `__enter__()`, usually `self`) in the order the context managers
            were added to this context. If this is a nested context, only return
            values of the inner-most scope by default.

            @param stack: The scope stack index. (default: -1)
            @return List of manmaged values.
        """
        return [value for context, value in self._context_stack[stack]]

    def value(self, index, stack=-1):
        """ Return a specific context value.

            @param index: Index within the 'values()' list. May also be a slice.
            @param stack: The scope stack index. (default: -1)
            @return List of manmaged values.
        """
        if isinstance(index, slice):
            return [x[1] for x in self._context_stack[stack][index]]
        else:
            return self._context_stack[stack][index][1]

    __getitem__ = value

    def __len__(self):
        """ Number of contexts in the current scope. """
        return len(self._context_stack[-1])

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

        if exc != (None, None, None):
            reraise(exc)

    def close(self):
        warnings.warn("Do not call close() on a Contexter.", DeprecationWarning)
        self.__exit__(None, None, None)


class _ExitDummy(object):
    def __init__(self, exit):
        self.exit = exit

    def __enter__(self):
        return self

    def __exit__(self, *exc):
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


contextmanager = contextlib.contextmanager


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
        @functools.wraps(func)
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
            self.entered = True
            return self.name

        def __exit__(self, *a):
            self.exited = a

    with Contexter(TestContext('a')) as ctx:
        assert ctx.values() == ['a']
        v1 = ctx.append(TestContext('b'))
        assert ctx.values() == ['a','b']
        assert v1 == 'b'
        v2 = ctx << TestContext('c')
        assert ctx.values() == ['a','b','c']
        assert v2 == 'c'
        assert ctx[0:2] == ['a','b']
        assert ctx[1:2] == ['b']
        assert ctx[1:] == ['b','c']
        assert ctx[-1] == 'c'
        assert ctx[-2:] == ['b','c']
        assert len(ctx) == 3

    with Contexter() as ctx:
        a, b, c = map(TestContext, 'abc')
        assert not a.entered
        assert not b.entered
        assert not c.entered

        ctx << a
        assert a.entered

        with ctx:
            ctx << b
            assert a.entered
            assert b.entered
            assert not c.entered

        assert a.entered
        assert b.entered and b.exited
        assert not c.entered
