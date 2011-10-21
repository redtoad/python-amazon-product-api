from amazonproduct import utils

DUMMY_CONFIG = """
# file: /etc/boto.cfg
[Credentials]
aws_access_key_id = global boto value
aws_secret_access_key = global boto value

# file: /home/user/.boto
[Credentials]
aws_access_key_id_ERROR = local boto value # the key is written incorrectly!
aws_secret_access_key = local boto value

# file: /home/user/.amazon-product-api
[Credentials]
aws_product_locale = de
"""

def test_load_config(configfiles):
    configfiles.load_from_string(DUMMY_CONFIG) 

    cfg = utils.load_config()
    assert set(cfg.keys()) == set(['access_key', 'secret_key', 'associate_tag',
                                   'locale'])

    assert cfg['access_key'] == 'global boto value'
    assert cfg['secret_key'] == 'local boto value'
    assert cfg['associate_tag'] is None
    assert cfg['locale'] == 'de'
