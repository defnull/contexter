==============================================
Contexter: contextlib for humanoids
==============================================

Contexter is a full replacement of the contextlib_ standard library module. It comes with more features, a nicer API and full support for Python 2.5 up to 3.x from a single source file.

To keep it short: Contexter allows you to nest and stack context managers in an easy and intuitive way. It is basically contextlib for humans.

Enough talk, let's see an example:

.. code:: python

    ''' Copy the content of one file to another
         and protect everything with a lock. '''

    with Contexter(lock) as ctx:
        in_file  = ctx << open('a.txt')
        out_file = ctx << open('b.txt', 'w')
        out_file.write(in_file.read())

Look at that. It's beautiful, isn't it? Let me explain: You call ``Contexter()`` with any number of context managers as arguments and later attach additional managers with the neat ``value = ctx << thing`` syntax. That's it. Only one level of indentation, no matter how many managers you need.

Just for comparison:

.. code:: python

    # Python 2.5 and 2.6
    with lock:
        with open('a.txt') as in_file:
            with open('b.txt', 'w') as out_file:
                out_file.write(in_file.read())

    # Starting with Python 2.7 and 3.2
    with lock, open('a.txt') as in_file, open('b.txt', 'w') as out_file:
        out_file.write(in_file.read())

    # Deprecated since Python 2.7 and 3.2
    with contextlib.nested(lock, open('a.txt'), open('b.txt', 'w')) as values:
        in_file, out_file = values
        out_file.write(in_file.read())

    # Since Python 3.3 (not backported to 2.7)
    with contextlib.ExitStack() as stack:
        stack.enter_context(lock)
        in_file  = stack.enter_context(open('a.txt'))
        out_file = stack.enter_context(open('b.txt', 'w'))
        out_file.write(in_file.read())


Replacing contextlib.nested_
====================================

You can use ``Contexter(*managers)`` as a drop-in replacement for ``contextlib.nested(*managers)``, just without the `confusing error prone quirks mentioned in the official documentation <contextlib.nested>`_.

Replacing contextlib.closing_
====================================

Just forget about it. Contexter turns close-able objects into context managers automatically.

Replacing contextlib.ExitStack_
======================================

Contexter offeres everything ``contextlib.ExitStack`` does (and more). If you want a drop-in replacement that also works for Python 2.x and 3.2, you can use our backported ``ExitStack``, a subclass of ``Contexter`` that is API compatible to the contextlib variant.

Replacing everything else from contextlib
=========================================

If you really want to stick with the standard API, you can. Contexter implements all public APIs from contextlib and backports new features as soon as they are introduced.

Links
======

.. target-notes::

.. _contextlib: http://docs.python.org/3/library/contextlib.html
.. _contextlib.nested: http://docs.python.org/2/library/contextlib.html#contextlib.nested
.. _contextlib.closing: http://docs.python.org/3/library/contextlib.html#contextlib.closing
.. _contextlib.ExitStack: http://docs.python.org/3/library/contextlib.html#contextlib.ExitStack

