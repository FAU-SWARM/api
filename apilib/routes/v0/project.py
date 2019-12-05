from __future__ import print_function, absolute_import
import os
import sys
import logging
import requests
import bson
from flask import (Blueprint, abort, request, jsonify, Response, session, current_app)

# database lib imports
from database.models.project import Project

# app imports
from apilib.lib import add_headers
from apilib.lib.exceptions import AugmentedException

FILE_DIR = os.path.dirname(__file__)
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

project_route = Blueprint('project_route', __name__)


@project_route.route('project', methods=['POST', 'GET', 'OPTIONS'])
@project_route.route('project/<project_id>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
def project(*args, **kwargs):
    args = current_app.config['args']
    headers = current_app.config['headers']

    response = Response()
    route_params = request.view_args
    get_params = request.args.to_dict(flat=False)
    if request.method in ['POST', 'PUT', 'DELETE']:
        body = request.json

    message = []
    data = None
    error = None
    try:
        if request.method == 'POST':
            body = request.json

            data = Project(**body)
            data.save()
            data = data.to_mongo()
        elif request.method == 'GET':
            _id = route_params.get('project_id')
            if _id is not None:
                data = Project.objects(id=bson.ObjectId(_id))
                if len(data) == 1:
                    data = data[0].to_mongo()
            else:
                data = [obj.to_mongo() for obj in Project.objects]

        elif request.method == 'PUT':
            body = request.json

            _id = route_params['project_id']
            data = Project.objects(id=bson.ObjectId(_id))
            data = data[0]
            for attr in ['name', 'description', 'img', 'link']:
                if body.get(attr) is not None:
                    setattr(data, attr, body[attr])
            data.save()
            data = data.to_mongo()
        elif request.method == 'DELETE':
            _id = route_params['project_id']
            data = Project.objects(id=bson.ObjectId(_id))
            data = [data.delete()]
        elif request.method == 'OPTIONS':
            pass
        else:
            pass

    except Exception as e:
        error = AugmentedException(e).to_dict()
        LOGGER.error('', exc_info=True)

    response = jsonify(message=message, data=data, error=error)
    response = add_headers(response, headers=headers)
    # LOGGER.warning(vars(response))
    return response