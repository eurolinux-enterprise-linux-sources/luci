# Copyright (C) 2009-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

"""Database Helpers used in luci."""

from luci.lib.helpers import ugettext as _
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
#from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.sql.expression import or_
from datetime import datetime

from luci.model import DBSession
import transaction
from luci.lib.cluster_status import ClusterStatus
from luci.model.objects import Node, Cluster, Task
from luci.model.auth import Group, User
import luci.lib.luci_tasks as lt
from luci.lib.cluster_permissions import permission_view

from luci.lib.ricci_communicator import RicciCommunicator
from luci.lib.ricci_defines import RICCI_BATCH_FAILURES_MAX, DEFAULT_RICCI_PORT
import luci.lib.ricci_queries as rq

import logging
log = logging.getLogger(__name__)

cluster_group_roles = [ 'view', 'membership', 'config', 'remove', 'node_cmd', 'service_cmd' ]

def get_cluster_db_obj(cluster_name):
    db_obj = None
    try:
        db_obj = DBSession.query(Cluster).filter_by(name=unicode(cluster_name)).one()
    except Exception, e:
        log.exception('Database object for cluster %s not found' % cluster_name)
    return db_obj

def get_cluster_node(cluster_name, node_name):
    db_obj = get_cluster_db_obj(cluster_name)
    if db_obj == None:
        return None
    for i in db_obj.nodes:
        if i.node_name == node_name:
            return i
    return None

def get_node_by_name(node_name):
    db_obj = None
    try:
        db_obj = DBSession.query(Node).filter_by(node_name=unicode(node_name)).one()
    except Exception, e:
        log.exception('Database node object with name %s not found' % node_name)
    return db_obj

def get_node_by_host(node_host):
    db_obj = None
    try:
        db_obj = DBSession.query(Node).filter_by(hostname=unicode(node_host)).one()
    except NoResultFound:
        log.debug('Database node object with host %s not found' % node_host)
    except Exception, e:
        log.exception('Database node object with host %s not found' % node_host)
    return db_obj

def get_agent_for_cluster(cluster_name):
    db_obj = get_cluster_db_obj(cluster_name)

    if db_obj is None:
        log.debug("Database object for cluster %s is missing" % cluster_name)
        return None

    # Try to use nodes that aren't busy first
    try:
        node_list = DBSession.query(Node).filter(Node.cluster.contains(db_obj)).order_by(Node.tasks != None).all()
    except:
        node_list = None

    if not node_list:
        node_list = db_obj.nodes

    node_list = db_obj.nodes
    if len(node_list) < 1:
        log.debug("No cluster nodes for cluster %s" % cluster_name)
        return None

    for node_obj in node_list:
        host = node_obj.hostname
        port = node_obj.port

        try:
            rc = RicciCommunicator(host, port)
            if rc is not None:
                if not rc.authed():
                    raise Exception, 'not authenticated'
            #cinfo = rc.cluster_info()
            #if not cinfo or not cinfo[0]:
            #    raise Exception, 'ricci reports host not in any cluster'
            #if cinfo[0].lower() != cluster_name.lower():
            #    raise Exception, 'ricci reports host in cluster %s not %s' \
            #            % (cinfo[0], cluster_name)
            return rc
        except Exception, e:
            log.exception('Error communicating with ricci agent at %s:%d: %s'
                % (host, port, e))

    log.error("Unable to communicate with ricci on any nodes in cluster %s"
        % cluster_name)
    return None

def get_model_for_cluster(cluster_name, rc=None):
    if rc is None:
        rc = get_agent_for_cluster(cluster_name)
        if rc is None:
            log.error("Unable to find a ricci agent for cluster %s"
                % cluster_name)
            return None

    try:
        from luci.lib.ClusterConf.ModelBuilder import ModelBuilder
        conf = rq.getClusterConf(rc)
        if conf is not None:
            model = ModelBuilder(conf, rc.cluster_version())
            return model
    except Exception, e:
        log.exception("Error getting cluster configuration for %s: %s"
            % (cluster_name, e))

    # Couldn't get the conf from any nodes
    return None

def get_cluster_status(rc):
    try:
        doc = rq.getClusterStatusBatch(rc)
    except Exception, e:
        log.exception('Error getting cluster status')
        return None
    return doc

def get_status_for_cluster(name, rc=None):
    if rc is None:
        rc = get_agent_for_cluster(name)

    if rc:
        status_xml = get_cluster_status(rc)
        if status_xml is None:
            log.debug("Error getting cluster status for %s" % name)
            return None
    else:
        status_xml = ''

    try:
        return ClusterStatus(status_xml)
    except Exception, e:
        log.exception("Error parsing status XML for cluster %s" % name)
        return None

def get_cluster_list():
    db_obj = None
    try:
        db_obj = DBSession.query(Cluster).all()
    except NoResultFound, e:
        log.error("No clusters found")
        return None
    except Exception, e:
        log.exception("Error accessing cluster database objects")
        return None

    return db_obj

def get_cluster_list_status(delegate=None):
    cluster_list = {}

    db_objs = get_cluster_list()
    for i in db_objs:
        cluster_name = i.name
        try:
            permission_view(cluster_name)
        except:
            continue
    
        # Delegate, if it exists, will be an instance of
        #   luci.controllers.cluster.IndividualClusterController
        if delegate and delegate.name == cluster_name:
            status = delegate.get_status()
        else:
            rc = get_agent_for_cluster(cluster_name)
            if rc is None:
                status = ClusterStatus(None)
            else:
                status = get_status_for_cluster(cluster_name, rc)

        cluster_list[cluster_name] = {
            'status': status
        }
    return cluster_list

def get_cluster_list_full():
    cluster_list = {}

    db_objs = get_cluster_list()
    if not db_objs:
        return cluster_list

    for i in db_objs:
        cluster_name = i.name
        try:
            permission_view(cluster_name)
        except:
            continue
        rc = get_agent_for_cluster(cluster_name)
        if rc is None:
            cluster_list[cluster_name] = {
                'model': None,
                'status': ClusterStatus(None)
            }
            continue
        cluster_list[cluster_name] = {
            'model': get_model_for_cluster(cluster_name, rc),
            'status': get_status_for_cluster(cluster_name, rc)
        }
    return cluster_list

def create_cluster_obj(cluster_name, node_list):
    try:
        db_obj = Cluster(name=unicode(cluster_name), display_name=unicode(cluster_name), nodes=[])
        DBSession.add(db_obj)
        for nodename, ricci_host, node_port in node_list:
            node_obj = Node(node_name=unicode(nodename),
                            hostname=unicode(ricci_host),
                            ipaddr=unicode(ricci_host),
                            display_name=unicode(nodename),
                            port=node_port,
                            cluster=[db_obj])
            DBSession.add(node_obj)
        db_create_cluster_roles(db_obj)
        DBSession.flush()
        #transaction.commit()
    except:
        log.exception("Error adding database objects for cluster: %s")
        DBSession.rollback()
        return False
        
    return True

def db_remove_cluster(cluster_name):
    db_obj = get_cluster_db_obj(cluster_name)
    if not db_obj:
        return False
    try:
        DBSession.refresh(db_obj)
        for i in db_obj.nodes:
            DBSession.delete(i)

        DBSession.refresh(db_obj)
        for i in db_obj.tasks:
            DBSession.delete(i)
        DBSession.delete(db_obj)

        for role in cluster_group_roles:
            cur_group = Group.by_group_name('%s_%s' % (role, cluster_name))
            if cur_group:
                DBSession.delete(cur_group)

        #DBSession.flush()
        transaction.commit()
    except:
        log.exception("Error removing cluster %s" % cluster_name)
        DBSession.rollback()
        return False
    return True

def db_remove_cluster_nodes(cluster_obj, node_list):
    kill_list = []

    DBSession.refresh(cluster_obj)
    try:
        for i in cluster_obj.nodes:
            if i.node_name in node_list or i.hostname in node_list:
                kill_list.append(i)
    except:
        log.exception('Error removing nodes "%s" from the database'
            % ', '.join(node_list))

    if len(kill_list) is not None:
        try:
            [DBSession.delete(i) for i in kill_list]
            DBSession.flush()
            #transaction.commit()
            return True
        except:
            log.exception('Error removing nodes "%s" from the database'
                % ', '.join(node_list))
    return False


def db_remove_task(task_obj):
    try:
        DBSession.delete(task_obj)
        DBSession.flush()
        return True
    except:
        log.exception('Error removing task object')
        DBSession.rollback()
    return False

def db_create_cluster_roles(cluster_obj):
    cluster_name = cluster_obj.name

    action_group = Group(group_name=u'view_%s' % cluster_name,
                     display_name=u'View/Monitor %s' % cluster_name)
    mem_group = Group(group_name=u'membership_%s' % cluster_name,
                     display_name=u'Add/Delete Nodes in %s' % cluster_name)
    config_group = Group(group_name=u'config_%s' % cluster_name,
                     display_name=u'Edit the Configuration for %s' % cluster_name)
    node_group = Group(group_name=u'node_cmd_%s' % cluster_name,
                     display_name=u'Start/Stop/Reboot Nodes in %s' % cluster_name)
    service_group = Group(group_name=u'service_cmd_%s' % cluster_name,
                     display_name=u'Enable/Disable/Relocate/Migrate Service Groups for %s' % cluster_name)
    remove_group = Group(group_name=u'remove_%s' % cluster_name,
                      display_name=u'Remove %s from the luci' % cluster_name)

    try:
        DBSession.add(action_group)
        DBSession.add(mem_group)
        DBSession.add(config_group)
        DBSession.add(node_group)
        DBSession.add(service_group)
        DBSession.add(remove_group)
        transaction.commit()
    except Exception, e:
        log.exception("Error adding group roles")
        DBSession.rollback()
        return False
    return True

def db_add_cluster_node(cluster_obj, name, ricci_host=None, ricci_port=None):
    if ricci_host is None:
        ricci_host = name
    node_obj = Node(node_name=unicode(name),
                    hostname=unicode(ricci_host),
                    ipaddr=unicode(ricci_host),
                    display_name=unicode(name),
                    port=ricci_port or DEFAULT_RICCI_PORT,
                    cluster=[cluster_obj])
    DBSession.add(node_obj)

# We keep a list of the nodes for each cluster (and some associated
# data (e.g., ricci hostname, ricci port) in our local database. If changes
# are made to the cluster membership outside of this luci instance, our
# node info may diverge from the info in the current cluster.conf.
# Consequentially, we need to reconcile the node list info we get from
# ricci (which it gets from modclusterd) with our database.
def reconcile_db_with_conf(cluster_name, conf_nodelist):
    cluster_obj = get_cluster_db_obj(cluster_name)
    if cluster_obj == None:
        # This should probably never happen.
        log.error('No cluster database object was found for cluster "%s"'
            % cluster_name)
        return None

    # If there are pending node deletions, hold off on removing what
    # appear to be stale nodes
    try:
        pending_deletes = DBSession.query(Task).with_parent(cluster_obj).filter(or_(Task.task_type == lt.TASK_CLUSTER_DEL_NODE, Task.task_type == lt.TASK_CLUSTER_DELETE)).count()
        if pending_deletes > 0:
            return True
    except:
        log.exception('counting deletion tasks')

    db_nodelist = set([i.node_name for i in cluster_obj.nodes])
    conf_nodelist = set(conf_nodelist)

    stale_nodes = db_nodelist - conf_nodelist
    if len(stale_nodes) > 0:
        # we need to purge the db objects for these (former) nodes
        ret = db_remove_cluster_nodes(cluster_obj, stale_nodes)
        if ret is not True:
            log.debug('An error occurred while attempting to remove stale DB objects for nodes "%s"' % ', '.join(stale_nodes))

    new_nodes = conf_nodelist - db_nodelist
    if len(new_nodes) > 0:
        # we need to create a new database entry for these nodes
        for i in new_nodes:
            db_add_cluster_node(cluster_obj, i)
        DBSession.flush()
        #transaction.commit()
    return conf_nodelist != db_nodelist

def luci_task_finish(cluster_name, node_name, task_db_obj, status):
    try:
        task_type = task_db_obj.task_type
        if len(task_db_obj.node) > 0:
            node_obj = task_db_obj.node[0]
        else:
            node_obj = None

        if node_obj and len(node_obj.cluster) > 0:
            cluster_obj = node_obj.cluster[0]
        elif cluster_name:
            cluster_obj = get_cluster_db_obj(cluster_name)
        else:
            cluster_obj = None

    except:
        log.exception('No node object for completed task %d'
            % task_db_obj.batch_id)
        node_obj = None

    db_remove_task(task_db_obj)

    if task_type == lt.TASK_CLUSTER_DEL_NODE:
        if status == 0:
            db_remove_cluster_nodes(cluster_obj, [ node_name ])
    elif task_type == lt.TASK_CLUSTER_DELETE:
        if status == 0:
            db_remove_cluster_nodes(cluster_obj, [ node_name ])

            cluster_obj = get_cluster_db_obj(cluster_name)
            DBSession.refresh(cluster_obj)

            if cluster_obj and len(cluster_obj.nodes) == 0:
                db_remove_cluster(cluster_name)
                return False
    return True

def get_cluster_task_status(cluster_name):
    task_status = {}

    db_obj = get_cluster_db_obj(cluster_name)
    if db_obj is None:
        return [0, task_status]

    tasks = db_obj.tasks
    if len(tasks) < 1:
        return [0, task_status]

    block_cluster = 0
    for t in tasks:
        DBSession.refresh(t)

        task_bid = str(t.batch_id)
        task_type = t.task_type
        
        try:
            node_obj = t.node[0]
        except:
            log.exception('No node object for task %s' % task_bid)
            db_remove_task(t)
            continue

        node_name = node_obj.node_name
        node_host = node_obj.hostname
        node_port = node_obj.port

        # return code = True denotes the cluster is blocked due to
        # a ricci job that is executing
        try:
            rc = RicciCommunicator(node_host, node_port)
            (ret_code, ret, modoff) = rc.batch_status(task_bid)

            ret['db_task_id'] = t.task_id
            if t.redirect_url:
                ret['redirect'] = t.redirect_url
            ret['db_status'] = t.status_msg
            ret['db_started'] = str(t.started)
            ret['db_task_type'] = task_type

            if ret_code == 0:
                if modoff < 1:
                    # the whole job completed successfully
                    ret['done'] = 1
                    luci_task_finish(cluster_name, node_name, t, 0)
                else:
                    t.batch_failures = 0
                    t.batch_status = 1
                    t.last_status = datetime.now()
                    if lt.luci_task_blocks_cluster(task_type):
                        block_cluster = 1
            elif ret_code == 1:
                # job is in progress
                t.batch_failures = 0
                t.batch_status = 1
                t.last_status = datetime.now()
                if lt.luci_task_blocks_cluster(task_type):
                    block_cluster = 1
            elif ret_code == -1:
                # job completed with errors
                ret['done'] = 1
                luci_task_finish(cluster_name, node_name, t, -1)
            elif ret_code == -2:
                # unable to retrieve the status of the batch job.
                # try again later.
                batch_failures = int(t.batch_failures) + 1
                if batch_failures >= RICCI_BATCH_FAILURES_MAX:
                    # give up
                    ret['done'] = 1
                    ret['status'] = _('Unable to retrieve the status for batch job %s after %d tries') % (task_bid, RICCI_BATCH_FAILURES_MAX)
                    luci_task_finish(cluster_name, node_name, t, -2)
                else:
                    t.batch_status = -2
                    t.batch_failures = batch_failures
                    t.last_status = datetime.now()
            else:
                # This should not happen. If it does, we should not allow it
                # to block the cluster.
                log.error('Unexpected response code for batch id %s from %s:%d %s'
                    % (task_bid, node_host, node_port, ret_code))
                ret['done'] = 1
                ret['status'] = _('Got unexpected return code %d when attempting to retrieve the status for batch id %s') % (ret_code, task_bid)
                luci_task_finish(cluster_name, node_name, t, -2)
            task_status[task_bid] = ret
        except:
            log.exception('Error getting status for %s on %s:%d' % (task_bid, node_host, node_port))
            t.batch_status = -2
            if lt.luci_task_blocks_cluster(task_type):
                block_cluster = 1
            task_status[task_bid] = {'status': _('Unable to retrieve the status for batch id %s on %s. The node may be temporarily unreachable') % (task_bid, node_host)}
            try:
                task_status[task_bid]['db_task_id'] = t.task_id
            except:
                pass

    try:
        DBSession.flush()
        #transaction.commit()
    except:
        log.exception('Error updating status objects')

    return [block_cluster, task_status]

def update_db_objects():
    # Update the current database, if it needs updating
    create_group = Group.by_group_name('create_cluster')
    if not create_group:
        create_group = Group(group_name=u'create_cluster',
                             display_name=u'create cluster role')
        DBSession.add(create_group)

    import_group = Group.by_group_name('import_cluster')
    if not import_group:
        import_group = Group(group_name=u'import_cluster',
                             display_name=u'import cluster role')
        DBSession.add(import_group)

    clusters = get_cluster_list()
    for obj in clusters:
        cur_name = obj.name
        for role in cluster_group_roles:
            try:
                grole = Group.by_group_name('%s_%s' % (role, cur_name))
            except:
                grole = None
            if not grole:
                grole = Group(group_name=u'%s_%s' % (role, cur_name),
                            display_name=u'%s role for %s' % (role, cur_name))
                DBSession.add(grole)
    transaction.commit()

def get_user_names():
    ret = []
    try:
        ret = [u.user_name for u in DBSession.query(User).all()]
    except:
        log.exception("Getting user names")
    return ret

def create_user_db_obj(username):
    db_obj = User(user_name=unicode(username),
                  email_address=unicode(username))
    try:
        DBSession.add(db_obj)
        DBSession.flush()
        return None
    except IntegrityError, ie:
        DBSession.rollback()
        log.exception('Error adding user %s' % username)
        return _("User %s already exists") % username
    except Exception, e:
        DBSession.rollback()
        log.exception('Error adding user %s' % username)
    return _("Unable to create user %s") % username

def get_user_roles(username):
    db_user = User.by_user_name(username)
    if not db_user:
        return []
    return [g.group_name for g in db_user.groups]

def grant_all_cluster_roles(username, clustername):
    if username == 'root':
        return True

    db_user = User.by_user_name(username)
    if not db_user:
        return False

    new_roles = []
    for role in cluster_group_roles:
        try:
            grole = Group.by_group_name('%s_%s' % (role, clustername))
            new_roles.append(grole)
        except:
            log.exception("Unknown group %s_%s" % (role, clustername))

    if len(new_roles) > 0:
        try:
            db_user.groups.extend(new_roles)
            DBSession.flush()
            transaction.commit()
            return True
        except:
            return False
    else:
        return False

def get_cluster_names():
    db_objs = get_cluster_list()
    if db_objs:
        return [c.name for c in db_objs]
    return []
