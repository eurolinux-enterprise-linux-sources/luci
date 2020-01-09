# Copyright (C) 2009-2010 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

# -*- coding: utf-8 -*-
"""The application's Globals object."""

from luci.lib.ricci_communicator import RicciCommunicator

__all__ = ['Globals']

class Globals(object):
    """Container for objects available throughout the life of the application.

    One instance of Globals is created during application initialization and
    is available during requests via the 'app_globals' variable.

    """
    DEFAULT_CLUSTER_VERSION = 3
    DEFAULT_CLUSTER_OS = 'Fedora'
    DEFAULT_OS_VERSION = None
    DEFAULT_RICCI_PORT = 11111

    def __init__(self):
        """Prepare some common static functions, constants etc."""
        self.data = None
        self.ricci_cache = {}
        self.conf_cache = {}

    def addRicciConnection(self, host, rc):
        self.ricci_cache[host] = rc

    def getRicciConnection(self, host, port=DEFAULT_RICCI_PORT):
        rc = RicciCommunicator(host, port)
        return rc
