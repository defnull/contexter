Contexter: A better contextlib
===============================================================================

Contexter is a full replacement of the contextlib_ standard library module. It comes with more features, a nicer API and full support for Python 2.5 up to 3.x from a single source file.

To keep it short: Contexter allows you to nest and stack context managers in an easy and intuitive way.

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
-------------------------------------------------------------------------------

You can use ``Contexter(*managers)`` as a drop-in replacement for ``contextlib.nested(*managers)``, just without the `confusing error prone quirks mentioned in the official documentation <contextlib.nested>`_.

Replacing contextlib.closing_
-------------------------------------------------------------------------------

Just forget about it. Contexter turns close-able objects into context managers automatically.

Replacing contextlib.ExitStack_
-------------------------------------------------------------------------------

Contexter offeres everything ``contextlib.ExitStack`` does (and more). If you want a drop-in replacement that also works for Python 2.x and 3.2, you can use our backported ``ExitStack``, a subclass of ``Contexter`` that is API compatible to the contextlib variant.

Replacing everything else from contextlib
-------------------------------------------------------------------------------

If you really want to stick with the standard API, you can. Contexter implements all public APIs from contextlib and backports new features as soon as they are introduced.


More examples:
-------------------------------------------------------------------------------

Contexter keeps track of the results of all invoked context managers. You can access the results later and don't have to unpack them all at the beginning.

.. code:: python

    with Contexter(open('a.txt'), open('b.txt', 'w')) as ctx:
        in_file, out_file = ctx.values()
        assert ctx.value(0) is in_file
        assert ctx[0] is in_file
        assert ctx[0:2] == [in_file, out_file]
        assert len(ctx) == 2

If you don't like the ``<<`` syntax, there is a method that does the same.

.. code:: python

    with Contexter() as ctx:
        in_file = ctx << open('a.txt')
        out_file = ctx.append(open('b.txt', 'w'))

Contexter contexts are nestable. Each level of nesting maintains its own stack of context managers and result values. This allows you to control the lifetime of contexts very precisely.

.. code:: python

    with Contexter() as ctx:
        out_file = ctx << open('b.txt', 'w')

        with ctx:
            in_file = ctx << open('a.txt')
            copy_data(in_file, out_file)

        assert in_file.closed == True
        assert out_file.closed == False

Links
-------------------------------------------------------------------------------

.. target-notes::

.. _contextlib: http://docs.python.org/3/library/contextlib.html
.. _contextlib.nested: http://docs.python.org/2/library/contextlib.html#contextlib.nested
.. _contextlib.closing: http://docs.python.org/3/library/contextlib.html#contextlib.closing
.. _contextlib.ExitStack: http://docs.python.org/3/library/contextlib.html#contextlib.ExitStack

