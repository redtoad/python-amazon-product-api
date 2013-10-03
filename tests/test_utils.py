import os
import pytest
import types

from amazonproduct import utils
from amazonproduct.processors import etree, minidom


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
# file: /etc/amazon-product-api.cfg
[Credentials]
access_key = global cfg value
secret_key = global cfg value

# file: ~/.amazon-product-api
[Credentials]
secret_key = local cfg value
locale = de

# file: ~/my-config
[Credentials]
secret_key = CUSTOM CONFIG OVERRIDES ALL!
"""


def test_load_config(configfiles, monkeypatch):
    configfiles.load_from_string(DUMMY_CONFIG)
    monkeypatch.setenv('AWS_LOCALE', 'OS VARIABLE')

    cfg = utils.load_config()
    assert set(cfg.keys()) == set([
        'access_key', 'secret_key', 'associate_tag', 'locale'])

    assert cfg['access_key'] == 'global cfg value'
    assert cfg['secret_key'] == 'local cfg value'
    assert cfg['associate_tag'] is None
    assert cfg['locale'] == 'OS VARIABLE'


def test_specific_config_file_overrides_all_but_os_variables(configfiles, monkeypatch):
    configfiles.load_from_string(DUMMY_CONFIG)
    monkeypatch.setenv('AWS_LOCALE', 'OS VARIABLE')

    path = configfiles.tmpdir.join(os.path.expanduser('~/my-config')).strpath
    cfg = utils.load_config(path)
    assert set(cfg.keys()) == set([
        'access_key', 'secret_key', 'associate_tag', 'locale'])

    assert cfg['secret_key'] == 'CUSTOM CONFIG OVERRIDES ALL!'
    assert cfg['access_key'] is None
    assert cfg['associate_tag'] is None
    assert cfg['locale'] == 'OS VARIABLE'


@pytest.mark.parametrize(('txt', 'cls'), [
    ('amazonproduct.processors.etree.Processor', etree.Processor),
    ('amazonproduct.processors.minidom.Processor', minidom.Processor),
])
def test_load_class(txt, cls):
    loaded = utils.load_class(txt)
    assert isinstance(loaded, types.TypeType)
    assert loaded == cls