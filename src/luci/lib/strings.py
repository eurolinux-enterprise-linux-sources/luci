# Copyright (C) 2009-2010 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

# -*- coding: utf-8 -*-

"""Common strings and short sentences presented to the user."""

from luci.lib.helpers import ugettext as _

__all__ = ['TitleStrings', 'VerboseStrings']


class TitleStrings:
    """Strings used in the title of the page.

    Final form of the title adjusted by 'luci.templates.title'.
    """

    # Following pairs are used for general items listing or certain entity
    # details displaying (thus, the '%s' is alias for the name of such entity)
    # respectively.

    CLUSTERS = _('clusters')
    CERTAIN_CLUSTER = _('cluster %s')

    NODES = _('nodes')
    CERTAIN_NODE = _('node %s')

    SERVICES = _('services')
    CERTAIN_SERVICE = _('service %s')

    FAILOVERS = _('failovers')
    CERTAIN_FAILOVER = _('failover %s')

    FENCES = _('fences')
    CERTAIN_FENCE = _('fence %s')

    STORAGE = _('storage')
    CERTAIN_STORAGE = _('storage %s')

    CONFIGURE = _('configure')


class VerboseStrings:
    """Strings used for error/warning/notice reporting to the user."""

    BAD_COMMAND_REQUEST = _('Bad command request.')
    INTERNAL_ERROR = _('Internal error.')
    NOTHING_CHOSEN = _('Nothing was chosen.')
