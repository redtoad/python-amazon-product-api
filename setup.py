from setuptools import setup

setup(
    name = 'python-amazon-product-api',
    version = '0.1',
    author = 'Sebastian Rahlf',
    author_email = 'basti AT redtoad DOT de',
    description = 'A Python wrappers for the Amazon Product Advertising API.', 
    py_modules = ['amazonproduct'],
    install_requires=['lxml>=2.1.5'],
    
    classifiers = [
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
