from __future__ import print_function, absolute_import
import os
import sys
import logging
import requests
from flask import (Blueprint, abort, request, jsonify, Response, session, current_app)


from database.models.raw_data import RawData

FILE_DIR = os.path.dirname(__file__)
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

raw_data_route = Blueprint('raw_data_route', __name__)

@raw_data_route.route('raw_data', methods=['POST', 'GET', 'OPTIONS'])
@raw_data_route.route('raw_data/<raw_data_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
def raw_data(*args, **kwargs):
    response = Response()
    route_params = request.view_args
    get_params = request.args.to_dict(flat=False)
    method = request.method

    if method == 'GET':
        raw_data = list(RawData.objects)
