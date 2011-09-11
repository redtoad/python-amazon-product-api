
def pytest_addoption(parser):
    parser.addoption('--locale', action='append', dest='locales',
        metavar='LOCALE', help='Locale to use (e.g. "de" or "us"). This option '
            'can be used more than once.')
    parser.addoption('--api-version', action='append', dest='versions',
        metavar='VERSION', help='API version to use (e.g. "2010-09-01"). This '
            'option can be used more than once.')