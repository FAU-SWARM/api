from __future__ import absolute_import, print_function, division, with_statement, unicode_literals
import os
import sys
import traceback
import logging
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class AugmentedException(Exception):
    def __init__(self, e, ignore=[], include=[]):
        # type: (Exception, List[str], List[str]) -> AugmentedException
        # we don't super on the Exception and just grind it up into something
        self.inner = None
        self.cause = None
        if isinstance(e, AugmentedException):
            # implying that e has already processed other exceptions prior
            self.inner = e

        self.type = e.__class__.__name__
        self.messages = []
        local_vars = {}
        if include or ignore:
            for key, value in e.__traceback__.tb_frame.f_locals.items():
                if include:
                    if key in include:
                        local_vars[key] = value
                elif ignore:
                    if key not in ignore:
                        local_vars[key] = value
                    else:
                        if key in local_vars:
                            del local_vars[key]
        if hasattr(e.__traceback__.tb_frame.f_code, 'co_filename'):
            filename = e.__traceback__.tb_frame.f_code.co_filename
        else:
            filename = None
        if hasattr(e.__traceback__.tb_frame.f_code, 'co_name'):
            funcname = e.__traceback__.tb_frame.f_code.co_name
        else:
            funcname = None
        if hasattr(e.__traceback__, 'tb_next') and hasattr(e.__traceback__.tb_next, 'tb_frame'):
            cause_locals = {}
            if include or ignore:
                for key, value in e.__traceback__.tb_next.tb_frame.f_locals.items():
                    if include:
                        if key in include:
                            cause_locals[key] = value
                    elif ignore:
                        if key not in ignore:
                            cause_locals[key] = value
                        else:
                            if key in local_vars:
                                del cause_locals[key]

            self.cause = dict(
                filename=e.__traceback__.tb_next.tb_frame.f_code.co_filename,
                funcname=e.__traceback__.tb_next.tb_frame.f_code.co_name,
                lineno=e.__traceback__.tb_next.tb_lineno,
                locals=cause_locals,
            )
            e.__traceback__.tb_frame.f_code.co_filename

        lineno = e.__traceback__.tb_lineno
        self.traceback = dict(
            filename=filename,
            funcname=funcname,
            lineno=lineno,
            locals=local_vars,
        )
        if isinstance(e, AugmentedException):
            self.messages += e.messages
        # has been creating a lot of bloat
        if hasattr(e, 'args') and not isinstance(e, AugmentedException):
            for arg in e.args:
                self.messages.append(arg)

    def __repr__(self):
        return str(self.to_dict())

    def __str__(self):
        return repr(self)

    def to_dict(self):
        return dict(
            type=self.type,
            traceback=self.traceback,
            messages=self.messages,
            inner=self.inner,
            cause=self.cause,
        )

    def append(self, data):
        # type: (Union[list, dict, Any]) -> None
        messages = {}
        if isinstance(data, list):
            messages = {str(i): datum for i, datum in enumerate(data)}
        elif isinstance(data, dict):
            messages = data
        else:
            messages = {data.__class__.__name__: data}

        self.messages.append(messages)