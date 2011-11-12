
.. _contributing:

How to contribute
=================

Development happens at http://bitbucket.org/basti/python-amazon-product-api.


Contributions are always welcome. You can do this by

* filing bug reports,
* discussing new ideas on the `mailing list`_ or
* sending me patches.

If you do the latter, please make sure that all the tests run successfully.

.. _mailing list: http://groups.google.com/group/python-amazon-product-api-devel


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

.. _pytest: http://pytest.org/
.. _tox: http://tox.testrun.org/