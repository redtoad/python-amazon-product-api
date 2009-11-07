from setuptools import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'python-amazon-product-api',
    version = '0.2',
    author = 'Sebastian Rahlf',
    author_email = 'basti AT redtoad DOT de',
    url="http://bitbucket.org/basti/python-amazon-product-api/downloads/",
    license='bsd',
    
    description = 'A Python wrappers for the Amazon Product Advertising API.', 
    long_description=read('README.rst'),
    keywords = 'amazon product advertising api wrapper',
    
    py_modules = ['amazonproduct'],
    install_requires=['lxml>=2.1.5'],
    
    classifiers = [
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
