#!/usr/bin/env python
# -*- coding: utf-8 -*-

# stdlib imports
from __future__ import absolute_import, print_function, division, with_statement, unicode_literals
import os
import sys
import json
import argparse
import datetime
import logging
from bson import ObjectId
from decimal import Decimal
from typing import Tuple, Any
from xml.etree.ElementTree import fromstring

# 3rd party imports
from mongoengine import Document
from xmljson import badgerfish, parker

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

DEFAULT_FORMAT = '%(levelname)s - %(name)s, line %(lineno)d - %(asctime)s: %(message)s'
ESSENTIAL_FORMAT = '%(levelname)s %(asctime)s - %(name)s, %(funcName)s, line: %(lineno)d - %(message)s '
VERBOSE_FORMAT = '%(levelname)s - %(processName)s - %(process)d %(funcName)s, line %(lineno)d - %(asctime)s: %(message)s'
DEFAULT_RIGID_FORMAT = '%(levelname)-10s - %(name)48s, line %(lineno)-4d - %(asctime)s: %(message)s'
VERBOSE_RIGID_FORMAT = '%(levelname)-10s - %(processName)-32s - pid: %(process)6d %(funcName)48s, line %(lineno)-4d - %(asctime)s: %(message)s'
VERBOSE_CSV_DEFAULT_FORMAT = '"%(levelname)s","%(processName)s","%(process)d","%(funcName)s","%(name)s","%(lineno)d","%(asctime)s","%(message)s"'
CSV_DEFAULT_FORMAT = '"%(levelname)s","%(name)s","%(lineno)d","%(asctime)s","%(message)s"'
MULTIPROCESS_DEFAULT_FORMAT = '%(levelname)-10s - %(processName)-32s - pid: %(process)6d - %(funcName)48s, line %(lineno)-4d - %(asctime)s: %(message)s'
GOD_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
GOD_FILE_FORMAT = '%Y-%m-%d-%H%M%S'


class AllEncoder(json.JSONEncoder):
    def default(self, o):
        '''must return a string printable dict'''
        # python-intel types that implement to_json():
        if hasattr(o, 'to_dict') and callable(o.to_dict):
            return o.to_dict()
        elif hasattr(o, 'to_json') and callable(o.to_json):
            return o.to_json()
        # catches namedtuples
        elif hasattr(o, '_asdict'):
            return o._asdict()
        elif isinstance(o, argparse.Namespace):
            return argparse_namespace_to_dict(o)
        elif isinstance(o, ObjectId):
            return str(o)
        elif isinstance(o, Document):
            return o.to_mongo().to_dict()
        elif isinstance(o, datetime.datetime):
            return str(o)
        elif isinstance(o, Exception):
            return '{} - {}'.format(o.__class__.__name__, str(o))
        elif isinstance(o, bytes):
            return o.hex()
        elif isinstance(o, Decimal):
            return float(o)
        else:
            return str(o)  # last ditch effort

        return json.JSONEncoder.default(self, o)

    def encode(self, obj):
        # https://github.com/python/cpython/blob/master/Lib/json/encoder.py
        if isinstance(obj, tuple) and hasattr(obj, '_asdict'):
            return super(AllEncoder, self).encode(obj._asdict())
        else:
            return super(AllEncoder, self).encode(obj)

    def _iterencode(self, obj, markers=None):
        # https://stackoverflow.com/a/5913148
        if isinstance(obj, tuple) and hasattr(obj, '_asdict'):
            gen = self._iterencode_dict(obj._asdict(), markers)
        else:
            gen = super(AllEncoder, self)._iterencode(self, obj, markers)
        for chunk in gen:
            yield chunk


# hack to override the default encoder by always passing AllEncoder
#   through to the json.dumps and dump functions.
setattr(json, '_dump_old', json.dump)
setattr(json, '_dumps_old', json.dumps)


def __override_json_dump(*args, **kwargs):
    kwargs['cls'] = AllEncoder
    kwargs['separators'] = (',', ':')
    return json._dump_old(*args, **kwargs)


def __override_json_dumps(*args, **kwargs):
    kwargs['cls'] = AllEncoder
    kwargs['separators'] = (',', ':')
    return json._dumps_old(*args, **kwargs)


setattr(json, 'dump', __override_json_dump)
setattr(json, 'dumps', __override_json_dumps)


def xml_to_json(path):
    with open(path, 'r') as r:
        root = fromstring(r.read())
        root_attributes = {key.lower(): value.lower() for key, value in root.attrib.items()}
        if 'convention' in root_attributes:
            convention = root_attributes['convention']
            if convention == 'parker':
                return parker.data(root)
        return badgerfish.data(root)


class DotDict(object):
    def __init__(self, *args, **kwargs):
        self.__attributes__ = set()  # invokes __setattr__
        super().__init__(*args, **kwargs)

    def __setattr__(self, name, value):
        if hasattr(self, '__attributes__'):
            self.__attributes__.add(name)
        return super().__setattr__(name, value)

    def to_dict(self):
        dick = {}
        for attr in self.__attributes__:
            value = getattr(self, attr)
            if isinstance(value, list):
                lst = []
                for v in value:
                    if isinstance(v, DotDict):
                        lst.append(v.to_dict())
                    else:
                        lst.append(v)
                value = lst
            elif isinstance(value, DotDict):
                value = value.to_dict()
            dick[attr] = value
        return dick


def dict_to_object(value):
    if isinstance(value, dict):
        obj = DotDict()
        for k, v in value.items():
            setattr(obj, k, dict_to_object(v))
        return obj
    elif isinstance(value, list):
        lst = []
        for v in value:
            lst.append(dict_to_object(v))
        return lst
    else:
        return value

    return obj


def argparse_namespace_to_dict(value):
    dick = {}
    for key, value in vars(value).items():
        if isinstance(value, dict):
            for k, v in value.items():
                dick[k] = v
        elif isinstance(value, list):
            lst = []
            for v in value:
                if isinstance(v, DotDict):
                    lst.append(v.to_dict())
                else:
                    lst.append(v)
            dick[key] = lst
        elif isinstance(value, DotDict):
            dick[key] = value.to_dict()
        else:
            dick[key] = value
    return dick


def console_log(lognames, level=logging.DEBUG, formatting=DEFAULT_FORMAT):
    # type: (List[str], int, str) -> None
    '''
    https://docs.python.org/3/library/logging.html#logrecord-attributes
    Examples:
        '%(name)-12s: %(levelname)-8s %(message)s'
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        '%(asctime)s %(name)s %(levelname)s %(message)s'
        '%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s'
        '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s \
%(message)s'
        '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'

        '%(relativeCreated)6d %(threadName)s %(message)s'
        '%(relativeCreated)5d %(name)-15s %(levelname)-8s %(message)s'
        '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d \
%(message)s'
        '%(asctime)s - %(levelname)-8s - %(filename)-16s - %(funcName)-16s - \
%(lineno)-4d - %(message)s'
    '''
    if isinstance(lognames, list):
        returnlogger = None
        hndl = logging.StreamHandler(sys.stdout)
        if formatting:
            formatter = logging.Formatter(formatting)
            hndl.setFormatter(formatter)
        for logname in lognames:
            logger = logging.getLogger(logname)
            logger.addHandler(hndl)
            logger.setLevel(level)
            if logname == __name__:
                returnlogger = logger
        return returnlogger


def file_log(
    lognames,
    level=logging.DEBUG,
    formatting=DEFAULT_FORMAT,
    filename='/var/log',
    mode='a',
):
    # type: (List[str], int, str, str, str) -> None
    '''https://docs.python.org/3/library/logging.handlers.html#filehandler'''
    filedir = os.path.dirname(filename)
    if not os.path.isdir(filedir):
        os.makedirs(filedir)

    if isinstance(lognames, list):
        returnlogger = None
        hndl = logging.FileHandler(filename, mode=mode)
        if formatting:
            formatter = logging.Formatter(formatting)
            hndl.setFormatter(formatter)
        for logname in lognames:
            logger = logging.getLogger(logname)
            logger.addHandler(hndl)
            logger.setLevel(level)
            if logname == __name__:
                returnlogger = logger
        return returnlogger


def add_headers(response, headers=[]):
    # type: (flask.wrappers.Response, List[Tuple[str, str]]) -> flask.wrappers.Response
    '''
    '''
    for header in headers:
        response.headers.add(*header)

    return response


def augment_args(args):
    if args.env:
        dick = xml_to_json(args.env)
        obj = dict_to_object(dick)
        dick = obj.to_dict()
        args.env = obj

    assert args.loglevel in list(logging._nameToLevel.keys())
    args.logdir = os.path.abspath(args.logdir)
    if not os.path.isdir(args.logdir):
        os.makedirs(args.logdir)
    args.logfile = os.path.join(
        args.logdir, 'api-{}.log'.format(datetime.datetime.now().strftime(GOD_FILE_FORMAT))
    )
    return args
