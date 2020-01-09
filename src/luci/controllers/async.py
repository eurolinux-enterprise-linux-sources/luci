# Copyright (C) 2009-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from tg import redirect, expose
from luci.lib.helpers import ugettext as _
from repoze.what.predicates import not_anonymous

from luci.lib.cluster_permissions import permission_view

from luci.lib.base import BaseController

__all__ = ['AsyncController']

class AsyncController(BaseController):
    allow_only = not_anonymous()

    @expose("json")
    def get_cluster_nodes(self, **kw):
        from luci.lib.async_helpers import get_node_list

        host = kw.get('host')
        if not host:
            return { 'errors': [ _('No host was given') ] }

        port = kw.get('port')
        if not port:
            return { 'errors': [ _('No port was given for host "%s"') % host ] }
        try:
            port = int(port)
            if port != port & 0xffff:
                raise ValueError, port
        except ValueError:
            return { 'errors': [ _('An invalid port "%s" was given for host "%s"') % (kw.get('port'), host) ] }

        passwd = kw.get('passwd')
        if not passwd:
            return { 'errors': [ _('No password was given for host "%s"') % host ] }
        return get_node_list(host, port, passwd)

    @expose("json")
    def is_cluster_busy(self, **kw):
        from luci.lib.async_helpers import cluster_is_busy
        cluster_name = kw.get('cluster')

        try:
            permission_view(cluster_name)
        except Exception, e:
            return {'code': -2, 'data': {'status': str(e)}}
        
        if not cluster_name:
            return {'code': -2, 'data': {'status': _('No cluster name was given')}}
        return cluster_is_busy(cluster_name)
