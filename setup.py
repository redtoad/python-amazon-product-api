#!/usr/bin/python

from setuptools import setup, find_packages
import os.path, sys

_here = os.path.abspath(os.path.dirname(__file__))

def version():
    # This rather complicated mechanism is employed to avoid importing any 
    # yet unfulfilled dependencies, for instance when installing under 
    # Python 2.4 from scratch
    import imp
    path = os.path.join(_here, 'amazonproduct', 'version.py')
    mod = imp.load_source('version', path)
    return mod.VERSION

def read(fname):
    # makes sure that setup can be executed from a different location
    return open(os.path.join(_here, fname)).read()

reqs = []
 # for python2.4
if sys.version_info[:2] < (2, 5):
    reqs += ['pycrypto']

setup(
    name = 'python-amazon-product-api',
    version = version(),
    author = 'Sebastian Rahlf',
    author_email = 'basti AT redtoad DOT de',
    url="http://bitbucket.org/basti/python-amazon-product-api/downloads/",
    license='bsd',

    description = 'A Python wrapper for the Amazon Product Advertising API.',
    long_description=read('README'),
    keywords = 'amazon product advertising api wrapper signed requests',

    packages = find_packages(_here, exclude=['tests']),
    install_requires=reqs,

    test_suite = 'tests',
    test_loader = 'tests:XMLResponseTestLoader',
    tests_require = ['nose', 'lxml>=2.1.5'],

    classifiers = [
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
