from __future__ import print_function, absolute_import
import os
import sys
import logging
import requests
import bson
from flask import (Blueprint, abort, request, jsonify, Response, session, current_app)

# app imports
from apilib.lib import add_headers
from apilib.lib.exceptions import AugmentedException

FILE_DIR = os.path.dirname(__file__)
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

ping_route = Blueprint('ping_route', __name__)


@ping_route.route('ping', methods=['POST', 'GET', 'PUT', 'DELETE', 'OPTIONS'])
def ping(*args, **kwargs):
    args = current_app.config['args']
    headers = current_app.config['headers']

    response = Response()
    route_params = request.view_args
    get_params = request.args.to_dict(flat=False)
    body = request.json

    message = [get_params, route_params, body]
    data = 'pong'
    error = None

    response = jsonify(message=message, data=data, error=error)
    response = add_headers(response, headers=headers)
    LOGGER.warning(vars(response))
    return response
