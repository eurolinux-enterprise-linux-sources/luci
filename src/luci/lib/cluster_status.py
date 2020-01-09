# Copyright (C) 2009-2010 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

import time
import datetime

import logging
log = logging.getLogger(__name__)

class NodeStatus:
    def __init__(self, node_xml):
        self.name = 'Unknown'
        self.clustered = 'Unknown'
        self.online = 'Unknown'
        self.uptime = 'Unknown'
        self.votes = 'Unknown'
        self.uptime_str = 'Unknown'
        self.nodeid = 'Unknown'
        self.services = {}

        try:
            self.name = node_xml.getAttribute('name')
            self.clustered = node_xml.getAttribute('clustered')
            self.online = node_xml.getAttribute('online')
            self.uptime = node_xml.getAttribute('uptime')
            self.votes = node_xml.getAttribute('votes')
            self.nodeid = node_xml.getAttribute('nodeid')
        except Exception, e:
            log.exception('Error parsing node status XML')
        try:
            tdelta = datetime.timedelta(0, int(self.uptime))
            self.uptime_str = '%02d:%s' % (tdelta.days, time.strftime('%H:%M:%S', time.gmtime(tdelta.seconds)))
        except:
            self.uptime_str = self.uptime 

class ServiceStatus:
    def __init__(self, svc_xml):
        self.type = 'service'
        self.name = 'Unknown'
        self.nodename = 'Unknown'
        self.running = 'Unknown'
        self.failed = 'Unknown'
        self.autostart = 'Unknown'
        self.is_vm = 'Unknown'

        try:
            self.name = svc_xml.getAttribute('name')
            self.nodename = svc_xml.getAttribute('nodename')
            self.running = svc_xml.getAttribute('running')
            self.failed = svc_xml.getAttribute('failed')
            self.autostart = svc_xml.getAttribute('autostart').lower() == 'true'
            self.is_vm = svc_xml.getAttribute('vm').lower() == 'true'
        except Exception, e:
            log.exception('Error parsing service status XML')

class ClusterStatus:
    def __init__(self, status_xml):
        self.nodes = {}
        self.services = {}

        self.alias = 'Unknown'
        self.name = 'Unknown'
        self.quorate = 'Unknown'
        self.votes = 'Unknown'
        self.minQuorum = 'Unknown'
        self.nodesJoined = 0
        self.nodesClustered = 0

        if not status_xml:
            return

        try:
            self.alias = status_xml.firstChild.getAttribute('alias')
            self.name = status_xml.firstChild.getAttribute('name')
            self.quorate = status_xml.firstChild.getAttribute('quorate')
            self.votes = status_xml.firstChild.getAttribute('votes')
            self.minQuorum = status_xml.firstChild.getAttribute('minQuorum')
        except Exception, e:
            log.exception('Error parsing cluster status XML')

        try:
            for node in status_xml.firstChild.childNodes:
                if node.nodeName == 'node':
                    ns = NodeStatus(node)
                    if ns.online.lower() == 'true':
                        self.nodesJoined += 1
                    if ns.clustered.lower() == 'true':
                        self.nodesClustered += 1
                    self.nodes[ns.name] = ns
        except Exception, e:
            log.exception('Error parsing node list')

        try:
            for node in status_xml.firstChild.childNodes:
                if node.nodeName == 'service':
                    ss = ServiceStatus(node)
                    self.services[ss.name] = ss
                    if ss.nodename:
                        self.nodes[ss.nodename].services[ss.name] = ss
        except Exception, e:
            log.exception('Error parsing service list')

    def getNodeStatus(self, nodename):
        ns = self.nodes.get(nodename)
        if ns:
            return ns

        for n in self.nodes.keys():
            if n in nodename or nodename in n:
                return self.nodes[n]
        return NodeStatus(None)
