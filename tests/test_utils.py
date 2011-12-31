from amazonproduct import utils

def test_load_global_boto_config(configfiles):
    configfiles.add_file('''
        [Credentials]
        aws_access_key_id = ABCDEFGH12345
        aws_secret_access_key = abcdegf43''', path='/etc/boto.cfg')

    cfg = utils.load_boto_config()
    assert cfg['access_key'] == 'ABCDEFGH12345'
    assert cfg['secret_key'] == 'abcdegf43'
    assert len(cfg) == 2

def test_load_local_boto_config(configfiles):
    configfiles.add_file('''
        [Credentials]
        aws_access_key_id = ABCDEFGH12345
        aws_secret_access_key = zhgsdds8''', path='~/.boto')

    cfg = utils.load_boto_config()
    assert cfg['access_key'] == 'ABCDEFGH12345'
    assert cfg['secret_key'] == 'zhgsdds8'
    assert len(cfg) == 2

def test_load_partial_boto_config(configfiles):
    configfiles.add_file('''
        [Credentials]
        aws_access_key_id = ABCDEFGH12345''', path='~/.boto')

    cfg = utils.load_boto_config()
    assert cfg['access_key'] == 'ABCDEFGH12345'
    assert len(cfg) == 1


def test_load_global_file_config(configfiles):
    configfiles.add_file('''
        [Credentials]
        access_key = ABCDEFGH12345
        secret_key = zhgsdds8''', path='/etc/amazon-product-api.cfg')

    cfg = utils.load_file_config()
    assert cfg['access_key'] == 'ABCDEFGH12345'
    assert cfg['secret_key'] == 'zhgsdds8'
    assert len(cfg) == 2

def test_load_local_file_config(configfiles):
    configfiles.add_file('''
        [Credentials]
        access_key = ABCDEFGH12345
        secret_key = zhgsdds8''', path='~/.amazon-product-api')

    cfg = utils.load_file_config()
    assert cfg['access_key'] == 'ABCDEFGH12345'
    assert cfg['secret_key'] == 'zhgsdds8'
    assert len(cfg) == 2


def test_load_environment_config(monkeypatch):
    monkeypatch.setenv('AWS_ACCESS_KEY', 'ABCDEFGH12345')
    monkeypatch.setenv('AWS_SECRET_ACCESS_KEY', 'zhgsdds8')
    monkeypatch.setenv('AWS_LOCALE', 'uk')

    cfg = utils.load_environment_config()
    assert cfg['access_key'] == 'ABCDEFGH12345'
    assert cfg['secret_key'] == 'zhgsdds8'
    assert cfg['locale'] == 'uk'
    assert not cfg.has_key('associate_tag')


DUMMY_CONFIG = """
# file: /etc/boto.cfg
[Credentials]
aws_access_key_id = global boto value
aws_secret_access_key = global boto value

# file: ~/.boto
[Credentials]
aws_access_key_id_wrongly_written = local boto value
aws_secret_access_key = local boto value

# file: ~/.amazon-product-api
[Credentials]
locale = de
"""

def test_load_config(configfiles, monkeypatch):
    configfiles.load_from_string(DUMMY_CONFIG)
    monkeypatch.setenv('AWS_LOCALE', 'OS VARIABLE')

    cfg = utils.load_config()
    assert set(cfg.keys()) == set([
        'access_key', 'secret_key', 'associate_tag', 'locale'])

    assert cfg['access_key'] == 'global boto value'
    assert cfg['secret_key'] == 'local boto value'
    assert cfg['associate_tag'] is None
    assert cfg['locale'] == 'OS VARIABLE'

