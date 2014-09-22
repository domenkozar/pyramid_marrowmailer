Pyramid integration package for "A highly efficient and modular mail delivery
framework for Python 2.6+ and 3.1+, formerly TurboMail."

Currently it must be used with ``pyramid_tm``, as ``.send()`` only works
if ``transaction``.commit() succeeded.

INSTALL
=======

::

    $ env/bin/easy_install pyramid_marrowmailer


USAGE
=====

If you have package installed, you can configure it in Pyramid like always::

    config.include('pyramid_marrowmailer')

All settings ``marrow.mailer`` expects are prefixed with ``mail.``. If you want
to use different prefix, set it with ``pyramid_marrowmailer.prefix``.

To see what options ``marrow.mailer`` support, see
`the documentation <https://github.com/marrow/marrow.mailer>`_. Note that
boolean options need a ``.on`` suffix. For example ``mail.transport.debug.on = true``.
Options that need to be converted to integer, add ``int`` suffix. For example
``mail.transport.port.int = 1337``.

``pyramid_marrowmailer`` calls ``Mailer.start`` when ``config.include('pyramid_marrowmailer')``
is called. ``atexit`` is used to register ``Mailer.stop`` to shutdown when wsgi server will exit.

Note that ``pyramid_marrowmailer`` subclasses ``marrow.mailer.Mailer`` to provide support for
``transaction``. Class is importable from ``pyramid_marrowmailer.TransactionMailer``.

You can accces ``pyramid_marrowmailer.TransactionMailer`` instance in two ways::

    message = request.mailer.new()
    ...
    message.send()


Or::
    
    from pyramid_marrowmailer import get_mailer
    mailer = get_mailer(request)
    message = mailer.new()
    ...
    message.send()


EXAMPLE
=======

If we have paster ``.ini`` something like::

    mail.mode = direct or transaction
    mail.transport.use = smtp
    mail.message.author = foobar@foo.com

Inside a view, we can do::

    message = request.mailer.new()
    message.subject = "foobar2"
    message.to = "foobar2@bar.com"
    message.plain = "hi"
    message.send()


TESTING
=======

::

    $ pip install nose coverage pep8 setuptools-flakes
    $ ./pre-commit-check.sh
