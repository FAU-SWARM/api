from __future__ import print_function, absolute_import
import os
import sys
import logging
import requests
import bson
from flask import (Blueprint, abort, request, jsonify, Response, session, current_app)

# database lib imports
from database.models.device import Device

# app imports
from apilib.lib import add_headers
from apilib.lib.exceptions import AugmentedException

FILE_DIR = os.path.dirname(__file__)
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

device_route = Blueprint('device_route', __name__)


@device_route.route('device', methods=['POST', 'GET', 'OPTIONS'])
@device_route.route('device/<device_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
def device(*args, **kwargs):
    args = current_app.config['args']
    headers = current_app.config['headers']

    response = Response()
    route_params = request.view_args
    get_params = request.args.to_dict(flat=False)
    body = request.json

    message = []
    data = None
    error = None
    try:
        if request.method == 'POST':
            data = Device(name=body['name'], meta_data=body['meta_data'])
            data.save()
        elif request.method == 'GET':
            data = list(Device.objects)
        elif request.method == 'PUT':
            _id = route_params['device_id']
            data = Device.objects(id=bson.ObjectId(_id))
            data.name = body['name']
            data.meta_data = body['meta_data']
            data.update()
        elif request.method == 'DELETE':
            _id = route_params['device_id']
            data = Device.objects(id=bson.ObjectId(_id))
            data.delete()
        elif request.method == 'OPTIONS':
            pass
        else:
            pass

    except Exception as e:
        error = AugmentedException(e).to_dict()
        LOGGER.error('', exc_info=True)

    response = jsonify(message=message, data=data, error=error)
    response = add_headers(response, headers=headers)
    return response