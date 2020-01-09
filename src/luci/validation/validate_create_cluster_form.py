# Copyright (C) 2009-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

# -*- coding: utf-8 -*-

from tg import flash, redirect, app_globals

from luci.lib.helpers import ugettext as _
from luci.model import DBSession
from luci.model.objects import Node, Cluster, Task

from luci.lib.ricci_helpers import send_batch_parallel, update_cluster_conf
from luci.lib.ricci_communicator import RicciCommunicator
from luci.lib.db_helpers import get_node_by_host, grant_all_cluster_roles, db_create_cluster_roles
from luci.lib.ClusterConf.ClusterNode import ClusterNode
import luci.lib.ricci_queries as rq

import luci.lib.luci_tasks as luci_tasks

#import transaction
import logging
log = logging.getLogger(__name__)

def validate_create_cluster_form(self, username, **kw):
    errors = []

    cluster_name = kw.get('cluster_name')
    if not cluster_name or len(cluster_name) < 1:
        flash(_('No cluster name was given'), 'error')
        return

    if len(cluster_name) > 15:
        flash(_('Cluster names must be less than 16 characters long'), 'error')
        return

    try:
        ret = int(DBSession.query(Cluster).filter_by(name=cluster_name).count())
        if ret != 0:
            flash(_('Luci is already managing a cluster named "%s"') % cluster_name, 'error')
            return
    except Exception, e:
        log.exception('Error querying the database while creating cluster %s' % cluster_name)
        flash(_('An error occurred while trying to query the luci database'), 'error')
        return

    enable_storage = kw.get('shared_storage') is not None
    reboot_nodes = kw.get('reboot_nodes') is not None
    download_pkgs = kw.get('download_pkgs') == 'download'
    all_passwd_same = kw.get('allSameCheckBox') is not None

    num_nodes = kw.get('num_nodes')
    if num_nodes:
        try:
            num_nodes = int(num_nodes) + 1
        except ValueError, e:
            num_nodes = None

    if not num_nodes:
        flash(_('No number of nodes was given'), 'error')
        return

    nodes = []
    first_passwd = None
    if all_passwd_same is True:
        for cur in xrange(num_nodes):
            cur_passwd = kw.get('password%d' % cur)
            if cur_passwd and not cur_passwd.isspace():
                first_passwd = cur_passwd
                break

    for cur in xrange(num_nodes):
        cur_nodename = kw.get('hostname%d' % cur)
        cur_ricci_host = kw.get('riccihost%d' % cur)
        cur_passwd = kw.get('password%d' % cur)
        cur_port = kw.get('port%d' % cur)

        if not cur_nodename or cur_nodename.isspace():
            continue
        if not cur_ricci_host or cur_ricci_host.isspace():
            cur_ricci_host = cur_nodename
        if not cur_port or cur_port.isspace():
            cur_port = str(app_globals.DEFAULT_RICCI_PORT)

        if not cur_passwd:
            if all_passwd_same and first_passwd is not None:
                cur_passwd = first_passwd
            else:
                errors.append(_('No password was provided for node "%s"') % cur_nodename)
                continue

        nodes.append([ cur_nodename, cur_ricci_host, cur_passwd, cur_port ])

    if len(nodes) < 1:
        errors.append(_('No cluster nodes were given'))

    if len(errors) > 0:
        flash(_('The following errors occurred while creating cluster "%s": %s')
            % (cluster_name, ', '.join(errors)), 'error')
        return

    cluster_db_obj = Cluster(name=cluster_name, display_name=cluster_name)

    node_list = []
    node_db_obj = {}
    task_db_obj = {}
    for node in nodes:
        try:
            rc = RicciCommunicator(node[1], port=int(node[3]))
            rc.auth(node[2])
            if not rc.authed():
                errors.append('Authentication to the ricci agent at %s:%s failed'
                    % (node[1], node[3]))
                continue

            rc = RicciCommunicator(node[1], port=int(node[3]))
            cur_cluster_name = rc.cluster_info()[0]
            if cur_cluster_name:
                errors.append('%s is already a member of a cluster named "%s"'
                    % (node[0], cur_cluster_name))
                continue

            node_list.append([node[1], node[3]])
            node_db_obj[node[0]] = Node(node_name=node[0],
                                        display_name=node[0],
                                        hostname=node[1],
                                        ipaddr=node[1],
                                        port=node[3])
            DBSession.add(node_db_obj[node[0]])
        except Exception, e:
            log.exception('Error adding node %s while creating cluster %s'
                % (node[0], cluster_name))
            errors.append(str(e))

    if len(errors) > 0:
        flash(_('The following errors occurred while creating cluster "%s": %s')
            % (cluster_name, ', '.join(errors)), 'error')
        DBSession.rollback()
        return

    host_triples = []
    node_names = [n[0] for n in nodes]
    for n in node_list:
        host_triples.append((n, rq.create_cluster,
            [ cluster_name, node_names,
              enable_storage, download_pkgs, reboot_nodes ]))
    ret = send_batch_parallel(host_triples, 10)

    for i in ret.iterkeys():
        if ret[i].has_key('error'):
           errors.append(_('Unable to connect to the ricci agent on node %s: %s') % (i, ret[i]['err_msg']))

        try:
            task_id = ret[i]['batch_result'][0]
            task_obj = Task(batch_id=task_id,
                        task_type=luci_tasks.TASK_CLUSTER_CREATE,
                        batch_status=1,
                        redirect_url='/cluster/%s/' % cluster_name,
                        status_msg=_('Creating node "%s" for cluster "%s"') % (i, cluster_name))
            DBSession.add(task_obj)
            task_db_obj[i] = task_obj
        except:
            log.exception('Error creating task object for %s' % i)

    try:
        cluster_db_obj.nodes = node_db_obj.values()
        cluster_db_obj.tasks = task_db_obj.values()
        for i in node_db_obj.iterkeys():
            cur_task_obj = task_db_obj.get(i)
            if not cur_task_obj:
                cur_task_obj = task_db_obj.get(node_db_obj[i].hostname)
            if cur_task_obj:
                node_db_obj[i].tasks = [ cur_task_obj ]
        db_create_cluster_roles(cluster_db_obj)
        DBSession.add(cluster_db_obj)
    except Exception, e:
        log.exception('Error updating luci DB for cluster %s' % cluster_name)
        DBSession.rollback()
        flash(_('An error occurred during the creation of cluster "%s" while updating the luci database: %s') % (cluster_name, str(e)), 'error')
        return

    try:
        DBSession.flush()
        #transaction.commit()
    except:
        log.exception('Error flushing DB while creating %s' % cluster_name)

    try:
        if username != 'root':
            grant_all_cluster_roles(username, cluster_name)
    except:
        log.exception("grant all cluster roles")
    flash(_('Creating the cluster "%s"...') % cluster_name, 'info')
    redirect("/cluster/%s" % cluster_name)

# TODO: refactor to share common bits with the validation for
#       cluster create

def validate_node_add_form(model, db_obj, **kw):
    errors = []

    if not model:
        flash(_('Unable to obtain the cluster configuration'), 'error')
        return

    cluster_name = model.getClusterName()

    enable_storage = kw.get('shared_storage') is not None
    reboot_nodes = kw.get('reboot_nodes') is not None
    download_pkgs = kw.get('download_pkgs') == 'download'
    num_nodes = kw.get('num_nodes')
    all_passwd_same = kw.get('allSameCheckBox') is not None

    if num_nodes:
        try:
            num_nodes = int(num_nodes) + 1
        except ValueError, e:
            num_nodes = None

    if not num_nodes:
        flash(_('No number of nodes was given'), 'error')
        return

    nodes = []
    first_passwd = None

    if all_passwd_same is True:
        for cur in xrange(num_nodes):
            cur_passwd = kw.get('password%d' % cur)
            if cur_passwd and not cur_passwd.isspace():
                first_passwd = cur_passwd
                break

    for cur in xrange(num_nodes):
        cur_nodename = kw.get('hostname%d' % cur)
        cur_ricci_host = kw.get('riccihost%d' % cur)
        cur_passwd = kw.get('password%d' % cur)
        cur_port = kw.get('port%d' % cur)

        if not cur_nodename or cur_nodename.isspace():
            continue
        if not cur_ricci_host or cur_ricci_host.isspace():
            cur_ricci_host = cur_nodename
        if not cur_port or cur_port.isspace():
            cur_port = str(app_globals.DEFAULT_RICCI_PORT)

        if not cur_passwd:
            if all_passwd_same and first_passwd is not None:
                cur_passwd = first_passwd
            else:
                errors.append(_('No password was provided for node "%s"') % cur_nodename)
                continue

        node_db_obj = get_node_by_host(cur_ricci_host)
        if node_db_obj is not None:
            errors.append(_('The host "%s" is already a member of cluster "%s"')
                % (cur_nodename, node_db_obj.cluster[0].name))

        nodes.append([ cur_nodename, cur_ricci_host, cur_passwd, cur_port ])

    if len(nodes) < 1:
        errors.append(_('No cluster nodes were given'))

    last_node_id = 0
    try:
        last_node_id = max([int(n.getNodeID()) for n in model.getNodes()])
    except:
        errors.append(_('Error getting node IDs for cluster %s') % cluster_name)
        log.exception('Error getting node IDs for cluster %s' % cluster_name)

    if len(errors) > 0:
        flash(_('The following errors occurred while adding nodes to cluster "%s": %s') % (cluster_name, ', '.join(errors)), 'error')
        return

    nodes_ptr = model.getClusterNodesPtr()
    node_list = []
    node_db_obj = {}
    task_db_obj = {}
    for node in nodes:
        try:
            rc = RicciCommunicator(node[1], port=int(node[3]))
            rc.auth(node[2])
            if not rc.authed():
                errors.append('Authentication to the ricci agent at %s:%s failed'
                    % (node[1], node[3]))
                continue

            rc = RicciCommunicator(node[1], port=int(node[3]))
            cur_cluster_name = rc.cluster_info()[0]
            if cur_cluster_name:
                errors.append('%s is already a member of a cluster named "%s"'
                    % (node[0], cur_cluster_name))
                continue

            node_list.append([node[1], node[3]])
            node_db_obj[node[0]] = Node(node_name=node[0],
                                        display_name=node[0],
                                        hostname=node[1],
                                        ipaddr=node[1],
                                        port=node[3])

            last_node_id += 1
            new_node = ClusterNode()
            new_node.setName(node[0])
            new_node.setNodeID(last_node_id)
            nodes_ptr.addChild(new_node)
        except Exception, e:
            log.exception('Error adding node %s to cluster %s'
                % (node[0], cluster_name))
            errors.append(str(e))

    if len(errors) == 0:
        model.getClusterPtr().incrementConfigVersion()
        model.lockConfigVersion()
        if update_cluster_conf(model) is not True:
            errors.append(_('Unable to update the cluster configuration on existing nodes'))

    if len(errors) > 0:
        flash(_('The following errors occurred while creating cluster "%s": %s')
            % (cluster_name, ', '.join(errors)), 'error')
        DBSession.rollback()
        return
    
    for i in node_db_obj.values():
        DBSession.add(i)
    db_obj.nodes.extend(node_db_obj.values())

    host_triples = []
    for n in node_list:
        host_triples.append((n, rq.create_cluster_nodes, 
                [ model, enable_storage, download_pkgs, reboot_nodes ]))
    ret = send_batch_parallel(host_triples, 10)

    for i in ret.iterkeys():
        if ret[i].has_key('error'):
           errors.append(_('Unable to connect to the ricci agent on node %s: %s') % (i, ret[i]['err_msg']))

        try:
            task_id = ret[i]['batch_result'][0]
            task_obj = Task(batch_id=task_id,
                        task_type=luci_tasks.TASK_CLUSTER_ADD_NODE,
                        batch_status=1,
                        redirect_url='/cluster/%s/' % cluster_name,
                        status_msg=_('Creating node "%s" for cluster "%s"') % (i, cluster_name))
            DBSession.add(task_obj)
            task_db_obj[i] = task_obj
        except:
            log.exception('Error creating task object for %s' % i)

    try:
        db_obj.tasks.extend(task_db_obj.values())
        for i in node_db_obj.iterkeys():
            cur_task_obj = task_db_obj.get(i)
            if not cur_task_obj:
                cur_task_obj = task_db_obj.get(node_db_obj[i].hostname)
            if cur_task_obj:
                node_db_obj[i].tasks = [ cur_task_obj ]
    except Exception, e:
        log.exception('Error updating luci DB for cluster %s' % cluster_name)
        flash(_('An error occurred while adding nodes to cluster "%s": %s') % (cluster_name, str(e)), 'error')
        return

    try:
        DBSession.flush()
        #transaction.commit()
    except:
        log.exception('Error updating luci DB for cluster %s' % cluster_name)
    flash(_('Creating nodes for cluster "%s"...') % cluster_name, 'info')
