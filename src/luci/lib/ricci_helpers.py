# Copyright (C) 2006-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

import threading

from luci.lib.helpers import ugettext as _

from luci.model import DBSession
from luci.model.objects import Task
from luci.lib.db_helpers import get_cluster_db_obj, get_node_by_host, get_agent_for_cluster, get_node_by_name
import luci.lib.ricci_queries as rq
import luci.lib.luci_tasks as luci_tasks
from luci.lib.ricci_communicator import RicciCommunicator

import logging
log = logging.getLogger(__name__)

class PWorker(threading.Thread):
    # triple := [ (host, port) function, *args ]
    def __init__(self, mutex, ret, host_triples, cluster_members_only=False):
        threading.Thread.__init__(self)
        self.mutex = mutex
        self.ret = ret
        self.triples = host_triples
        self.cluster_members_only = cluster_members_only

    def run(self):
        while True:
            self.mutex.acquire()
            if len(self.triples) == 0:
                self.mutex.release()
                return
            triple = self.triples.pop()
            self.mutex.release()

            r = { 'ricci': None }

            try:
                rc = RicciCommunicator(triple[0][0], triple[0][1])
                r['ricci'] = rc
                if self.cluster_members_only is True:
                    cinfo = rc.cluster_info()
                    if not cinfo or not cinfo[1]:
                        r['error'] = True
                        r['err_msg'] = 'not in cluster'
                        r['ricci'] = None
                        continue

                if triple[1] is not None:
                    if triple[2]:
                        args = list(triple[2])
                    else:
                        args = list()
                    args.insert(0, rc)
                    r['batch_result'] = triple[1](*args)
            except Exception, e:
                r['error'] = True
                r['err_msg'] = str(e)
                r['ricci'] = None
                log.error('%s' % str(e))

            self.mutex.acquire()
            self.ret[triple[0][0]] = r
            self.mutex.release()

def send_batch_parallel(triples, max_threads, cluster_members_only=False):
    mutex = threading.RLock()
    threads = list()
    num_trips = 0
    trips = list()
    ret = {}

    for trip in triples:
        trips.append(trip)
        num_trips += 1
        if num_trips <= max_threads:
            threads.append(PWorker(mutex, ret, triples, cluster_members_only))

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return ret

# Pass an empty node_list to send to all cluster nodes
def prepare_host_triples(cluster_obj, node_list, fn, *args):
    host_triples = []
    for node_obj in cluster_obj.nodes:
        if len(node_list) == 0 or node_obj.node_name in node_list or node_obj.hostname in node_list:
            node_host = node_obj.hostname
            node_port = node_obj.port
            host_triples.append(( ( node_host, node_port ), fn, args))
    return host_triples

def update_cluster_conf(cluster_model, node_list=[]):
    cluster_name = cluster_model.getClusterName()
    cluster_obj = get_cluster_db_obj(cluster_name)
    if not cluster_obj:
        return False

    conf_str = cluster_model.exportModelAsString()
    if cluster_model.getClusterVersion() < 3:
        # Pick one node and set the "propagate" variable to true. ccs_tool
        # will distribute the conf and activate the new version.
        try:
            rc = get_agent_for_cluster(cluster_name)
            ret = rq.setClusterConfSync(get_agent_for_cluster(cluster_name), conf_str)
            if ret != True:
                log.info('Config update for %s failed at node %s' \
                    % (cluster_name, rc.hostname()))
                return False
        except Exception, e:
            log.exception('Config update for %s failed' % cluster_name)
            return False
    else:
        # For >= cluster3, RHEL6 set the conf on each node, then activate
        # the new version.
        host_triples = prepare_host_triples(cluster_obj, node_list, rq.setClusterConf, conf_str)
        try:
            ret = send_batch_parallel(host_triples, 10, True)
        except Exception, e:
            log.exception('error updating cluster config for "%s"' \
                % cluster_name)
            return False

        for i in ret.keys():
            try:
                batch_status = ret[i].get('batch_result')
                if batch_status:
                    batch_num = batch_status[0]
                    node_obj = get_node_by_host(i)
                    task_obj = Task(batch_id=int(batch_num),
                                task_type=luci_tasks.TASK_CLUSTER_UPDATE_CONF,
                                batch_status=-1,
                                status_msg=_('Updating the cluster configuration for cluster "%s" on node "%s"') % (cluster_name, i))
                    cluster_obj.tasks.append(task_obj)
                    node_obj.tasks.append(task_obj)
                    DBSession.add(task_obj)
                else:
                    if ret[i].get('error'):
                        log.error('Error retrieving batch number from %s: %s' %
                            (i, ret[i].get('err_msg')))
            except Exception, e:
                log.exception('Unable to retrieve the batch number from %s' % i)
                continue

        # Activate the new config we just set
        new_version = cluster_model.getClusterConfigVersion()
        host_triples = prepare_host_triples(cluster_obj, node_list, rq.setClusterVersion, new_version)

        try:
            ret = send_batch_parallel(host_triples, 10, True)
        except Exception, e:
            log.exception('Error activating new config for "%s"' % cluster_name)
            return False

        for i in ret.keys():
            try:
                batch_status = ret[i].get('batch_result')
                if batch_status:
                    batch_num = batch_status[0]
                    node_obj = get_node_by_host(i)
                    task_obj = Task(batch_id=int(batch_num),
                                task_type=luci_tasks.TASK_CLUSTER_ACTIVATE_CONF,
                                batch_status=-1,
                                status_msg=_('Activating configuration version %s for cluster "%s" on node "%s"') % (new_version, cluster_name, i))
                    cluster_obj.tasks.append(task_obj)
                    node_obj.tasks.append(task_obj)
                    DBSession.add(task_obj)
                else:
                    if ret[i].get('error'):
                        log.error('Error retrieving batch number from %s: %s' %
                            (i, ret[i].get('err_msg')))
            except Exception, e:
                log.exception('Unable to retrieve the batch number from %s' % i)
                continue

    return True

def cluster_start(cluster_name):
    cluster_obj = get_cluster_db_obj(cluster_name)
    if not cluster_obj:
        return False

    host_triples = prepare_host_triples(cluster_obj, [], rq.nodeJoinCluster, True, False)

    try:
        ret = send_batch_parallel(host_triples, 10)
    except Exception, e:
        log.exception('An error occurred while updating the cluster configuration for cluster "%s"'
            % cluster_name)
        return False

    for i in ret.keys():
        try:
            batch_status = ret[i].get('batch_result')
            batch_num = batch_status[0]
            node_obj = get_node_by_host(i)
            task_obj = Task(batch_id=int(batch_num),
                            task_type=luci_tasks.TASK_CLUSTER_START,
                            batch_status=-1,
                            status_msg=_('Starting cluster "%s" -- Starting node "%s"') % (cluster_name, i))
            cluster_obj.tasks.append(task_obj)
            node_obj.tasks.append(task_obj)
            DBSession.add(task_obj)
        except Exception, e:
            log.exception('Unable to retrieve the batch number from %s' % i)
            continue
    return True

def cluster_stop(cluster_name):
    cluster_obj = get_cluster_db_obj(cluster_name)
    if not cluster_obj:
        return False

    host_triples = prepare_host_triples(cluster_obj, [], rq.nodeLeaveCluster, True, False, False)

    try:
        ret = send_batch_parallel(host_triples, 10)
    except Exception, e:
        log.exception('An error occurred while stopping cluster "%s"' % cluster_name)
        return False

    for i in ret.keys():
        try:
            batch_status = ret[i].get('batch_result')
            batch_num = batch_status[0]
            node_obj = get_node_by_host(i)
            task_obj = Task(batch_id=int(batch_num),
                            task_type=luci_tasks.TASK_CLUSTER_STOP,
                            batch_status=-1,
                            status_msg=_('Stopping cluster "%s" -- Stopping node "%s"') % (cluster_name, i))
            cluster_obj.tasks.append(task_obj)
            node_obj.tasks.append(task_obj)
            DBSession.add(task_obj)
        except Exception, e:
            log.exception('Unable to retrieve the batch number from %s' % i)
            continue
    return True

def cluster_delete(cluster_name):
    cluster_obj = get_cluster_db_obj(cluster_name)
    if not cluster_obj:
        return False

    host_triples = prepare_host_triples(cluster_obj, [], rq.nodeLeaveCluster, True, True, True)

    try:
        ret = send_batch_parallel(host_triples, 10)
    except Exception, e:
        log.exception('An error occurred while deleting cluster "%s"' % cluster_name)
        return False

    ret_code = True
    for i in ret.keys():
        try:
            batch_status = ret[i].get('batch_result')
            batch_num = batch_status[0]
            node_obj = get_node_by_host(i)
            task_obj = Task(batch_id=int(batch_num),
                            task_type=luci_tasks.TASK_CLUSTER_DELETE,
                            redirect_url='/cluster/%s/' % cluster_name,
                            batch_status=-1,
                            status_msg=_('Deleting cluster "%s" -- Deleting node "%s"') % (cluster_name, i))
            cluster_obj.tasks.append(task_obj)
            node_obj.tasks.append(task_obj)
            DBSession.add(task_obj)
        except Exception, e:
            log.exception('Unable to retrieve the batch number from %s' % i)
            ret_code = False
            continue
    return ret_code

def cluster_restart(cluster_name):
    cluster_stop(cluster_name)
    cluster_start(cluster_name)
    return True

def cluster_node_start(cluster_name, node_list):
    cluster_obj = get_cluster_db_obj(cluster_name)
    if not cluster_obj:
        return False

    host_triples = prepare_host_triples(cluster_obj, node_list,
                    rq.nodeJoinCluster, False, False)

    try:
        ret = send_batch_parallel(host_triples, 10)
    except Exception, e:
        log.exception('An error occurred while starting cluster "%s" node "%s"'
            % (cluster_name, node_list))
        return False

    for i in ret.keys():
        try:
            batch_status = ret[i].get('batch_result')
            batch_num = batch_status[0]
            node_obj = get_node_by_host(i)
            task_obj = Task(batch_id=int(batch_num),
                            task_type=luci_tasks.TASK_CLUSTER_NODE_START,
                            batch_status=-1,
                            status_msg=_('Starting cluster "%s" node "%s"') % (cluster_name, i))

            cluster_obj.tasks.append(task_obj)
            node_obj.tasks.append(task_obj)
            DBSession.add(task_obj)
        except Exception, e:
            log.exception('Unable to retrieve the batch number from %s' % i)
            continue
    return True

def cluster_node_stop(cluster_name, node_list):
    cluster_obj = get_cluster_db_obj(cluster_name)
    if not cluster_obj:
        return False

    host_triples = prepare_host_triples(cluster_obj, node_list,
                    rq.nodeLeaveCluster, False, False, False)

    try:
        ret = send_batch_parallel(host_triples, 10)
    except Exception, e:
        log.exception('An error occurred while stopping cluster "%s" nodes "%s"'
            % (cluster_name, node_list))
        return False

    for i in ret.keys():
        try:
            batch_status = ret[i].get('batch_result')
            batch_num = batch_status[0]
            node_obj = get_node_by_host(i)
            task_obj = Task(batch_id=int(batch_num),
                            task_type=luci_tasks.TASK_CLUSTER_NODE_STOP,
                            batch_status=-1,
                            status_msg=_('Stopping cluster "%s" node "%s"') % (cluster_name, i))
            cluster_obj.tasks.append(task_obj)
            node_obj.tasks.append(task_obj)
            DBSession.add(task_obj)
        except Exception, e:
            log.exception('Unable to retrieve the batch number from %s' % i)
            continue
    return True

def cluster_node_restart(cluster_name, node_list):
    cluster_node_stop(cluster_name, node_list)
    cluster_node_start(cluster_name, node_list)
    return True

def cluster_node_reboot(cluster_name, node_list):
    cluster_obj = get_cluster_db_obj(cluster_name)
    if not cluster_obj:
        return False

    host_triples = prepare_host_triples(cluster_obj, node_list, rq.nodeReboot)

    try:
        ret = send_batch_parallel(host_triples, 10)
    except Exception, e:
        log.exception('An error occurred while rebooting node %s in cluster "%s"'
            % (node_list, cluster_name))
        return False

    for i in ret.keys():
        try:
            batch_status = ret[i].get('batch_result')
            batch_num = batch_status[0]
            node_obj = get_node_by_host(i)
            task_obj = Task(batch_id=int(batch_num),
                            task_type=luci_tasks.TASK_CLUSTER_NODE_REBOOT,
                            batch_status=-1,
                            status_msg=_('Rebooting node "%s"') % i)
            cluster_obj.tasks.append(task_obj)
            node_obj.tasks.append(task_obj)
            DBSession.add(task_obj)
        except Exception, e:
            log.exception('Unable to retrieve the batch number from %s' % i)
            continue
    return True

def cluster_node_delete(cluster_name, cluster_model, node_list):
    cluster_obj = get_cluster_db_obj(cluster_name)
    if not cluster_obj:
        return False

    try:
        for node in node_list:
            cluster_model.deleteNodeByName(node)
    except Exception, e:
        log.exception('Unable to delete node "%s" from the cluster configuration' % node)
        return False

    host_triples = prepare_host_triples(cluster_obj, node_list,
                    rq.nodeLeaveCluster, False, True, True)

    try:
        ret = send_batch_parallel(host_triples, 10)
    except Exception, e:
        log.exception('An error occurred while deleting "%s" nodes "%s"'
            % (cluster_name, node_list))
        return False

    for i in ret.keys():
        try:
            batch_status = ret[i].get('batch_result')
            batch_num = batch_status[0]
            node_obj = get_node_by_host(i)
            task_obj = Task(batch_id=int(batch_num),
                            task_type=luci_tasks.TASK_CLUSTER_DEL_NODE,
                            redirect_url='/cluster/%s/' % cluster_name,
                            batch_status=-1,
                            status_msg=_('Deleting cluster "%s" node "%s"') % (cluster_name, i))
            cluster_obj.tasks.append(task_obj)
            node_obj.tasks.append(task_obj)
            DBSession.add(task_obj)
        except Exception, e:
            log.exception('Unable to retrieve the batch number from %s' % i)
            continue

    try:
        update_cluster_conf(cluster_model, node_list=cluster_model.getNodeNames())
    except:
        log.exception('Unable to delete nodes "%s" from the cluster configuration' % ', '.join(node_list))


def cluster_svc_start(cluster_name, svc_name, target_node=None):
    cluster_obj = get_cluster_db_obj(cluster_name)
    if not cluster_obj:
        return False
    rc = get_agent_for_cluster(cluster_name)
    if rc is None:
        log.error('No ricci agent for cluster "%s" could be found' % cluster_name)
        return False
    node_obj = get_node_by_host(rc.hostname())
    if not node_obj:
        return False
    try:
        (batch_num, batch_status) = rq.startService(rc, svc_name, target_node)
        task_obj = Task(batch_id=int(batch_num),
                        task_type=luci_tasks.TASK_CLUSTER_SVC_START,
                        batch_status=batch_status,
                        status_msg=_('Starting cluster "%s" service "%s" from node "%s"') \
                            % (cluster_name, svc_name, rc.hostname()))
        cluster_obj.tasks.append(task_obj)
        node_obj.tasks.append(task_obj)
        DBSession.add(task_obj)
    except Exception, e:
        log.exception('Unable to retrieve the batch number from %s' % rc.hostname())
    return True

def cluster_svc_restart(cluster_name, svc_name):
    cluster_obj = get_cluster_db_obj(cluster_name)
    if not cluster_obj:
        return False
    rc = get_agent_for_cluster(cluster_name)
    if rc is None:
        log.error('No ricci agent for cluster "%s" could be found' % cluster_name)
        return False
    node_obj = get_node_by_host(rc.hostname())
    if not node_obj:
        return False
    try:
        (batch_num, batch_status) = rq.restartService(rc, svc_name)
        task_obj = Task(batch_id=int(batch_num),
                        task_type=luci_tasks.TASK_CLUSTER_SVC_RESTART,
                        batch_status=batch_status,
                        status_msg=_('Restarting cluster "%s" service "%s" from node "%s"') \
                            % (cluster_name, svc_name, rc.hostname()))
        cluster_obj.tasks.append(task_obj)
        node_obj.tasks.append(task_obj)
        DBSession.add(task_obj)
    except Exception, e:
        log.exception('Unable to retrieve the batch number from %s' % rc.hostname())
    return True

def cluster_svc_disable(cluster_name, svc_name):
    cluster_obj = get_cluster_db_obj(cluster_name)
    if not cluster_obj:
        return False
    rc = get_agent_for_cluster(cluster_name)
    if rc is None:
        log.error('No ricci agent for cluster "%s" could be found' % cluster_name)
        return False
    node_obj = get_node_by_host(rc.hostname())
    if not node_obj:
        return False
    try:
        (batch_num, batch_status) = rq.stopService(rc, svc_name)
        task_obj = Task(batch_id=int(batch_num),
                        task_type=luci_tasks.TASK_CLUSTER_SVC_DISABLE,
                        batch_status=batch_status,
                        status_msg=_('Disabling cluster "%s" service "%s" from node "%s"') \
                            % (cluster_name, svc_name, rc.hostname()))
        cluster_obj.tasks.append(task_obj)
        node_obj.tasks.append(task_obj)
        DBSession.add(task_obj)
    except Exception, e:
        log.exception('Unable to retrieve the batch number from %s' % rc.hostname())
    return True

def cluster_svc_migrate(cluster_name, svc_name, target_node):
    cluster_obj = get_cluster_db_obj(cluster_name)
    if not cluster_obj:
        return False
    rc = get_agent_for_cluster(cluster_name)
    if rc is None:
        log.error('No ricci agent for cluster "%s" could be found' % cluster_name)
        return False
    node_obj = get_node_by_host(rc.hostname())
    if not node_obj:
        return False
    try:
        (batch_num, batch_status) = rq.migrateService(rc, svc_name, target_node)
        task_obj = Task(batch_id=int(batch_num),
                        task_type=luci_tasks.TASK_CLUSTER_SVC_MIGRATE,
                        batch_status=batch_status,
                        status_msg=_('Migrating cluster "%s" VM service "%s" to node "%s"') \
                            % (cluster_name, svc_name, target_node))
        cluster_obj.tasks.append(task_obj)
        node_obj.tasks.append(task_obj)
        DBSession.add(task_obj)
    except Exception, e:
        log.exception('Unable to retrieve the batch number from %s' % rc.hostname())
    return True

def node_get_daemon_states(node, daemon_list):
    node_host = ''
    try:
        db_obj = get_node_by_name(node)
        node_host = db_obj.hostname
        node_port = db_obj.port
        rc = RicciCommunicator(node_host, node_port)
        ret = rq.getDaemonStates(rc, daemon_list)
    except Exception, e:
        return {'errors': _('Unable to retrieve daemon states from %s: %s') %
                            (node_host, str(e.args))}
    else:
        return ret
