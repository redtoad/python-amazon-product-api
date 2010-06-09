#!/usr/bin/python

from setuptools import setup
import os

import amazonproduct

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'python-amazon-product-api',
    version = amazonproduct.__version__,
    author = 'Sebastian Rahlf',
    author_email = 'basti AT redtoad DOT de',
    url="http://bitbucket.org/basti/python-amazon-product-api/downloads/",
    license='bsd',
    
    description = 'A Python wrapper for the Amazon Product Advertising API.', 
    long_description=read('README'),
    keywords = 'amazon product advertising api wrapper signed requests',
    
    py_modules = ['amazonproduct'],
    install_requires=['lxml>=2.1.5'], # 'pycrypto' # for python2.4

    test_suite = 'tests',
    test_loader = 'tests:XMLResponseTestLoader',
    tests_require = 'nose',

    classifiers = [
        'Operating System :: OS Independent', 
        'Development Status :: 3 - Alpha', 
        'Intended Audience :: Developers', 
        'License :: OSI Approved :: BSD License', 
        'Operating System :: OS Independent', 
        'Programming Language :: Python :: 2.4', 
        'Programming Language :: Python :: 2.5', 
        'Programming Language :: Python :: 2.6', 
        'Topic :: Internet :: WWW/HTTP', 
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
