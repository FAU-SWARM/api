from __future__ import print_function, absolute_import
import os
import sys
import logging
import requests
from flask import (Blueprint, abort, request, jsonify, Response, session, current_app)

FILE_DIR = os.path.dirname(__file__)
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

device_route = Blueprint('device_route', __name__)

@device_route.route('device', methods=['POST', 'GET', 'PUT', 'DELETE', 'OPTIONS'])
@device_route.route('device/<device_id>', methods=['POST', 'GET', 'PUT', 'DELETE', 'OPTIONS'])
def device(*args, **kwargs):
    response = Response()
    route_params = request.view_args
    get_params = request.args.to_dict(flat=False)
    method = request.method


