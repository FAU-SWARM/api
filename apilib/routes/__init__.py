import logging
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

HEADERS = [
    ('Access-Control-Allow-Methods', 'GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'),
    ('Access-Control-Allow-Credentials', 'true'),
    ('Access-Control-Allow-Headers', 'Content-Type, Authorization, Credentials'),
]

HEADERS_DEV = [
    ('Access-Control-Allow-Origin', '*')
]