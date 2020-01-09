# Copyright (C) 2009-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from luci.lib.helpers import ugettext as _

from luci.lib.ricci_communicator import RicciCommunicator
import luci.lib.ricci_queries as rq

from luci.lib.cluster_conf_helpers import get_cluster_conf_nodes
from luci.lib.db_helpers import get_cluster_task_status, get_cluster_db_obj

import logging
log = logging.getLogger(__name__)

def get_node_list(host, port, passwd):
    node_names = None
    cluster_name = None

    try:
        rc = RicciCommunicator(host, port)
        rc.auth(passwd)
        if not rc.authed():
            return { 'errors': [ _('Authentication to host "%s" failed') % host ]}

        cluster_name = rc.cluster_info()[0]
        if not cluster_name:
            return { 'errors': [_('Host "%s" is not a member of a cluster') % host ] }

        db_obj = get_cluster_db_obj(cluster_name)
        if db_obj is not None:
            return { 'errors': [_('A cluster named "%s" has already been added') % cluster_name ] }

        conf_xml = rq.getClusterConf(rc)
        if conf_xml:
            node_names = get_cluster_conf_nodes(conf_xml)

        if not node_names or len(node_names) < 1:
            return { 'errors': [ _('Unable to retrieve the list of cluster nodes from "%s"') % host ]}
    except Exception, e:
        log.exception('Unable to connect to %s' % host)
        # Presumably only RicciError or RicciQueriesError could be caught, both of which
        # have exactly one argument.
        return { 'errors': [ _('Unable to connect to host "%s": %s') % (host, e.args[0]) ] }
    return { 'nodes': node_names, 'cluster': cluster_name }

def cluster_is_busy(cluster_name):
    try:
        ret = get_cluster_task_status(cluster_name)
        if len(ret[1]) > 0:
            return {'code': ret[0], 'data': ret[1]}
        else:
            return {'code': ret[0]}
    except Exception, e:
        ret = {'code': -1, 'data': {'status': unicode(e) }}
    return ret
