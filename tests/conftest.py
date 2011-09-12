
def pytest_addoption(parser):
    group = parser.getgroup('amazonproduct',
        'custom options for testing python-amazon-product-api')
    group._addoption('--locale', action='append', dest='locales',
        metavar='LOCALE', help='Locale to use (e.g. "de" or "us"). This option '
            'can be used more than once. Note that tests with specific locales '
            'defined which do not match the ones specified by this option will '
            'NOT be run.')
    group._addoption('--api-version', action='append', dest='versions',
        metavar='VERSION', help='API version to use (e.g. "2010-09-01"). This '
            'option can be used more than once. Note that tests with specific '
            'versions defined which do not match the ones specified by this '
            'option will NOT be run.')
