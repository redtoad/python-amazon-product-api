
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
    group._addoption('--refetch', action='store', type='choice', dest='fetch',
        metavar='method', choices=['no', 'missing', 'outdated', 'all'],
        default='no', help='Fetch responses from live server and overwrite '
            'previously cached XML file: one of no (default)|missing|outdated|'
            'all.')

def pytest_funcarg__server(request):
    """
    Is the same as funcarg `httpserver` from plugin pytest-localserver with the
    difference that it has a module-wide scope.
    """
    def setup():
        try:
            localserver = request.config.pluginmanager.getplugin('localserver')
        except KeyError:
            raise pytest.skip('This test needs plugin pytest-localserver!')
        server = localserver.http.Server()
        server.start()
        return server
    def teardown(server):
        server.stop()
    return request.cached_setup(setup, teardown, 'module')

