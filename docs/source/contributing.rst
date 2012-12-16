
.. _contributing:

How to contribute
=================

Development happens at http://bitbucket.org/basti/python-amazon-product-api.

Contributions are always welcome. You can do this by

* filing bug reports,
* discussing new ideas on the `mailing list`_ or
* sending me patches.

If you do the latter, please make sure that all the tests run successfully (see
also :ref:`running-the-tests`).

.. _mailing list: http://groups.google.com/group/python-amazon-product-api-devel


Setting up a development environment
------------------------------------

What you will need to work on this module:

* `lxml`_
* `pytest`_ (>2.0)
* `pytest-localserver`_
* `Sphinx`_
* `tox`_ (optional)

It might be a good idea to install all of the above mentioned dependencies into
a `virtualenv`_ (I prefer to use `virtualenvwrapper`_).


.. _running-the-tests:

Running the Tests
-----------------

There are a large number of tests to check for inter-version and inter-locale
consistencies. The simplest way of running them is to run ::

    python setup.py test

in the root directory. The tests require `pytest`_. In order to check all
supported Python versions (currently 2.4 - 2.7), I use tox_.

When adding new tests, you need to pass your credentials to the API. Have a look
at :ref:`config` to see how to set it up. Your credentials will *not be stored*
in any files!

.. note:: Providing tests with your pull request will increase the chances of
   your changes being accepted by a factor of one gazillion!


.. _lxml: http://lxml.de
.. _pytest-localserver: http://pypi.python.org/pypi/pytest-localserver
.. _Sphinx: http://sphinx.pocoo.org/
.. _pytest: http://pytest.org/
.. _tox: http://tox.testrun.org/
.. _virtualenv: http://www.virtualenv.org/
.. _virtualenvwrapper: http://www.doughellmann.com/projects/virtualenvwrapper/

