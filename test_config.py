from config import DefaultUndertakerConfigLoader, DefaultUndertakersConfigLoader, DefaultKeywordsConfigLoader, \
    EmailConfigLoader, DefaultConfigLoaderFactory


def test_default_undertaker_config_loader():
    undertaker_config_dict = {'identifier': 'identifier', 'base_url': 'base_url'}
    undertaker_config_loader = DefaultUndertakerConfigLoader()
    undertaker_config = undertaker_config_loader.load(undertaker_config_dict)

    assert 'identifier' == undertaker_config.identifier
    assert 'base_url' == undertaker_config.base_url


def test_default_undertakers_config_loader():
    undertakers_config_list = [
        {'identifier': 'identifier1', 'base_url': 'base_url1'},
        {'identifier': 'identifier2', 'base_url': 'base_url2'}
    ]

    undertakers_config_loader = DefaultUndertakersConfigLoader(DefaultUndertakerConfigLoader())
    undertakers_config = undertakers_config_loader.load(undertakers_config_list)

    assert 'identifier1' == undertakers_config.undertakers[0].identifier
    assert 'base_url1' == undertakers_config.undertakers[0].base_url

    assert 'identifier2' == undertakers_config.undertakers[1].identifier
    assert 'base_url2' == undertakers_config.undertakers[1].base_url


def test_default_keywords_config_loader():
    keywords_config_list = ['keyword1', 'keyword2', 'keyword3']

    keywords_config_loader = DefaultKeywordsConfigLoader()
    keywords_config = keywords_config_loader.load(keywords_config_list)

    assert 'keyword1' == keywords_config.keywords[0]
    assert 'keyword2' == keywords_config.keywords[1]
    assert 'keyword3' == keywords_config.keywords[2]


def test_email_config_loader():
    email_config_dict = {
        'server_address': 'server_address',
        'server_port': 111,
        'sender_address': 'sender_address',
        'sender_password': 'sender_password',
        'receiver_addresses': [
            'receiver_address1',
            'receiver_address2'
        ]
    }

    email_config_loader = EmailConfigLoader()
    email_config = email_config_loader.load(email_config_dict)

    assert 'server_address' == email_config.server_address
    assert 111 == email_config.server_port
    assert 'sender_address' == email_config.sender_address
    assert 'sender_password' == email_config.sender_password
    assert 'receiver_address1' == email_config.receiver_addresses[0]
    assert 'receiver_address2' == email_config.receiver_addresses[1]

