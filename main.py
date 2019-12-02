from __future__ import print_function, absolute_import
import os
import sys
import ssl
import datetime
import argparse
import logging
from pathlib import Path

# 3rd party imports
from flask import (Flask, request, jsonify, Response, session, redirect, url_for)
from mongoengine import connect

# app imports
from apilib.lib import (
    json, AllEncoder, xml_to_json, dict_to_object,
    console_log, file_log,
    GOD_FILE_FORMAT, GOD_FORMAT,
    augment_args
)
from apilib.routes.v0 import ping_route
from apilib.routes.v0.authorization import authorization_route
from apilib.routes.v0.device import device_route
from apilib.routes.v0.raw_data import raw_data_route
from apilib.routes.v0.project import project_route
from apilib.routes.v0.user import user_route


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def main(args):
    # type: (argparse.Namespace) -> None

    console_log([__name__, 'flask', 'apilib', 'database'], level=args.loglevel)
    file_log([__name__, 'flask', 'apilib', 'database'], level=args.loglevel, filename=args.logfile)
    LOGGER.info('log at {}'.format(args.logfile))

    app = Flask(__name__)
    app.logger = LOGGER
    app.json_encoder = AllEncoder

    API_ENDPOINT = args.env.api.endpoint
    API_PORT = args.env.api.port
    WEB_URI = args.env.website.endpoint

    HEADERS = [
        ('Access-Control-Allow-Methods', 'GET, POST, PATCH, PUT, DELETE, OPTIONS'),
        ('Access-Control-Allow-Credentials', 'true'),
    ]
    if args.dev:
        if args.local:
            HEADERS.insert(0, ('Access-Control-Allow-Origin', '*'))
        else:
            HEADERS.insert(0, ('Access-Control-Allow-Origin', 'http://localhost:4200'))
            HEADERS.append(('Access-Control-Allow-Headers', 'Content-Type, Authorization, Credentials')),
    else:
        HEADERS.insert(0, ('Access-Control-Allow-Origin', '{}'.format(WEB_URI)))
        HEADERS.append(('Access-Control-Allow-Headers', 'Content-Type, Authorization, Credentials')),

    app.config['args'] = args
    app.config['headers'] = HEADERS
    app.config['SESSION_TYPE'] = 'filesystem'

    # v0
    app.register_blueprint(ping_route, url_prefix='/{}'.format(API_ENDPOINT))
    app.register_blueprint(authorization_route, url_prefix='/{}'.format(API_ENDPOINT))
    app.register_blueprint(device_route, url_prefix='/{}'.format(API_ENDPOINT))
    app.register_blueprint(raw_data_route, url_prefix='/{}'.format(API_ENDPOINT))
    app.register_blueprint(project_route, url_prefix='/{}'.format(API_ENDPOINT))
    app.register_blueprint(user_route, url_prefix='/{}'.format(API_ENDPOINT))

    # v1

    kwargs = dict(
        port=API_PORT,
        debug=args.debug,
        host='0.0.0.0',
    )

    # db connection
    connect(
        db=args.env.database.name,
        # username='user',
        # password='12345',
        host=args.env.database.hostname,
        port=args.env.database.port,
    )

    try:
        LOGGER.debug(
            json.dumps(args, indent=4)
        )
        LOGGER.debug(app.url_map)
        app.run(**kwargs)
    except KeyboardInterrupt:
        LOGGER.warning('ctrl+c detected!')
        exit(0)
    except Exception as e:
        raise e


if __name__ == "__main__":
    # parse the args
    parser = argparse.ArgumentParser()
    development = parser.add_argument_group()
    development.add_argument('-d', '--dev', action='store_true', help='Enable dev mode.')
    development.add_argument('--debug', action='store_true', help='Set the flask debug flag hi or low.')
    development.add_argument('--local', action='store_true', help='Set the network and cors to respect localhost.')

    execution = parser.add_argument_group()
    execution.add_argument('-e', '--env', action='store_true', default=os.path.abspath('env.xml'), help='Env XML File')

    logstuff = parser.add_argument_group()
    logstuff.add_argument('--loglevel', type=str, default='DEBUG', help='python logging level')
    logstuff.add_argument('--logdir', type=str, default='/var/log/swarm', help='python logging path')

    args = augment_args(parser.parse_args())

    print(vars(args))

    main(args)
