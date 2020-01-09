# Copyright (C) 2009-2010 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

# -*- coding: utf-8 -*-
"""The base Controller API."""

from tg import TGController, request, tmpl_context

__all__ = ['BaseController', 'SubController']

class BaseController(TGController):
    """Base class for the root controller.

    The root of the application is used to compute URLs used by this app.

    """

    def __call__(self, environ, start_response):
        """Invoke the Controller."""
        # TGController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']

        request.identity = request.environ.get('repoze.who.identity')
        tmpl_context.identity = request.identity
        return TGController.__call__(self, environ, start_response)


class SubController(object):
    """Base class for subcontrollers.

    Keyword arguments passed on object creation are automatically moved
    inside the object as its attributes.

    """

    def __new__(cls, *args, **kwargs):
        # If the class that invoked this method is directly inherited from
        # this class, set new attributes according to passed keyword arguments
        # and delegate this invocation upwards (omitting the level
        # of SubController class).
        # Then delegate the invocation to superclass.

        if cls.__base__.__name__ == 'SubController':
            for kw, v in kwargs.iteritems():
                setattr(cls, kw, v)
            kwargs.clear()
        return super(type(cls), cls).__new__(cls, *args)
