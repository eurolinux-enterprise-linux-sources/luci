# Copyright (C) 2009-2010 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

import logging
log = logging.getLogger(__name__)

def get_cluster_conf_nodes(conf_xml):
    try:
        cluster_nodes = conf_xml.getElementsByTagName('clusternode')
        return map(lambda x: str(x.getAttribute('name')), cluster_nodes)
    except Exception, e:
        log.exception('Error getting node list')
    return None
