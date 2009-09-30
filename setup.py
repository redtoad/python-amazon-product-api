from setuptools import setup

setup(
    name = "amazon",
    version = '0.1',
    author = 'Sebastian Rahlf',
    author_email = 'basti AT redtoad DOT de',
    description = 'A collection of wrappers for various Amazon Webservices.',
    
    packages = ['amazon'],
    install_requires=['lxml>=2.1.5'],
    
    classifiers = [
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
