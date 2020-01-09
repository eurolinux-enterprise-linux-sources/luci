# Copyright (C) 2009-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

# -*- coding: utf-8 -*-
"""Cluster controller module"""

# turbogears imports
from tg import request, expose, redirect, flash, app_globals, tmpl_context, require

# third party imports
from repoze.what.predicates import not_anonymous, in_any_group, is_user, Any, NotAuthorizedError
from luci.lib.helpers import ugettext as _

# project specific imports
from luci.lib.base import BaseController
from luci.lib.db_helpers import get_cluster_list, get_model_for_cluster, get_status_for_cluster, db_remove_cluster, get_agent_for_cluster, get_cluster_db_obj, reconcile_db_with_conf
from luci.lib.cluster_permissions import permission_remove, permission_svc_cmd, permission_config, permission_membership, permission_node_cmd, permission_view
import luci.lib.ricci_helpers as rh
from luci.lib.flash2 import flash2
import luci.validation.validate_cluster_prop as vcp
from luci.validation.validate_create_cluster_form import validate_create_cluster_form, validate_node_add_form
from luci.validation.validate_fence import validateNewFenceDevice, validateFenceDevice
from luci.validation.validate_resource import validate_clusvc_form, validate_resource_form
from luci.lib.ClusterConf.Method import Method
from luci.lib.ClusterConf.Unfence import Unfence
from luci.validation.validate_fence import validate_fenceinstance
from urllib import unquote_plus

import logging
log = logging.getLogger(__name__)

data = app_globals.data

class ClusterController(BaseController):
    allow_only = not_anonymous()
    tmpl_context.show_sidebar = True

    @expose('luci.templates.cluster_list')
    def index(self):
        tmpl_context.manage_clusters = True
        tmpl_context.show_sidebar = True
        return dict(page='cluster', clusterpage='clusterpage')

    @expose('luci.templates.cluster_list')
    @require(Any(is_user('root'),
                 in_any_group('managers', 'create_cluster'),
             msg=_("You must be an administrator or be granted access to create clusters")))
    def create_cmd(self, command=None, **kw):
        try:
            identity = request.environ.get('repoze.who.identity')
            username = identity['repoze.who.userid']
        except:
            username = None
            log.exception("Error getting current username")
        validate_create_cluster_form(self, username, **kw)
        return dict(use_referrer=False, page='cluster', clusterpage='clusterpage')

    @expose('luci.templates.cluster_list')
    def delete_cmd(self, command=None, **kw):
        if 'MultiAction' in kw:
            command = kw['MultiAction']
            for key, element in kw.items():
                if element == "on":
                    try:
                        permission_remove(key)
                        db_remove_cluster(unicode(key))
                    except NotAuthorizedError, e:
                        flash(e, status="warning")
        redirect('/cluster/')

    @expose()
    def lookup(self, name, *args):
        name = unquote_plus(name)
        cluster_list = get_cluster_list() or []
        for i in cluster_list:
            if i.name == name:
                try:
                    permission_view(name)
                    icc = IndividualClusterController(name, data)
                    return icc, args
                except NotAuthorizedError, e:
                    flash(e, status="warning")
        cc = ClusterController
        #flash(("No cluster named \"%s\" is managed by luci") % name,
        #    status='error')
        redirect('/cluster/')
        return (cc, args)

class IndividualClusterController(BaseController):
    def __init__(self, name, iccdata, nodename=None):
        self.agent  = None
        self.model  = None
        self.status = None
        self.version = None
        self.OS = None
        self.OSVersion = None

        self.name = name
        self.data = iccdata
        self.nodename = nodename

        identity = request.environ.get('repoze.who.identity')
        self.username = identity['repoze.who.userid']

        tmpl_context.show_sidebar = True
        tmpl_context.cluster_name = self.name
        tmpl_context.cluster_url = '/cluster/%s/' % self.name
        tmpl_context.cluster = self

    @expose("luci.templates.node")
    def index(self):
        try:
            permission_view(self.name)
        except NotAuthorizedError, e:
            flash(e, status="warning")
            redirect("/")
 
        db = get_cluster_db_obj(self.name)

        return dict(page='nodes', name=self.nodename, base_url='/nodes', nodes=db.nodes)

    def get_agent(self):
        if not self.agent:
            try:
                self.agent = get_agent_for_cluster(self.name)
            except:
                self.agent = None
        return self.agent

    def get_model(self):
        if not self.model:
            try:
                self.model = get_model_for_cluster(self.name, self.get_agent())
                if self.model:
                    reconcile_db_with_conf(self.name, self.model.getNodeNames())
            except:
                log.exception("Error reconciling db with conf")
        return self.model

    def get_status(self):
        if not self.status:
            self.status = get_status_for_cluster(self.name, self.get_agent())
        return self.status

    def get_version(self):
        if not self.version:
            self.version = app_globals.DEFAULT_CLUSTER_VERSION
            m = self.get_model()
            if m:
                self.version = m.getClusterVersion()

        return self.version

    def get_OS(self):
        if not self.OS:
            self.OS = app_globals.DEFAULT_CLUSTER_OS
            m = self.get_model()
            if m:
                self.OS = m.getClusterOS()

        return self.OS

    def get_OSVersion(self):
        if not self.OSVersion:
            self.OS = app_globals.DEFAULT_OS_VERSION
            m = self.get_model()
            if m:
                self.OSVersion = m.getOSVersion()

        return self.OSVersion
    
    @expose("luci.templates.node")
    def nodes(self):
        try:
            permission_view(self.name)
        except NotAuthorizedError, e:
            flash(e, status="warning")
            redirect("/")
 
        db = get_cluster_db_obj(self.name)
        return dict(use_referrer=False, page='nodes', name=self.nodename, base_url='/nodes', nodes=db.nodes)

    @expose("luci.templates.node")
    def add_nodes_cmd(self, command=None, **kw):
        try:
            permission_membership(self.name)
        except NotAuthorizedError, e:
            flash(e, status="warning")
            redirect('%s%s' % (tmpl_context.cluster_url, 'nodes'))
 
        self.get_model()
        db = get_cluster_db_obj(self.name)
        vret = validate_node_add_form(self.model, db, **kw)
        redirect('%s%s' % (tmpl_context.cluster_url, 'nodes'))

    @expose("luci.templates.node")
    def nodes_fence_cmd(self, command=None, **kw):
        cur_nodename = kw.get('node')

        try:
            permission_config(self.name)
        except NotAuthorizedError, e:
            flash(e, status="warning")
            redirect('%s%s' % (tmpl_context.cluster_url, cur_nodename))
 
        self.get_model()
        if not self.model:
            flash(_('Unable to contact any nodes in this cluster'),
                status="error")
            redirect(tmpl_context.cluster_url)

        if kw.get("method_to_remove"):
            node = self.model.retrieveNodeByName(cur_nodename)
            methodname = kw.get("method_to_remove")
            found_method = False
            for child in node.getFenceNode().getChildren():
                if child.getName() == methodname:
                    for child_device in child.getChildren():
                        node.removeFenceInstance(child, child_device)
                    found_method = True
                    node.getFenceNode().removeChild(child)
                    break
            if found_method is True:
                log.info('User "%s" removed method "%s" from node "%s" in cluster "%s"'
                    % (self.username, methodname, cur_nodename, self.name))
                rh.update_cluster_conf(self.model)
            else:
                log.error('User "%s" failed to remove method "%s" from node "%s" in cluster "%s"'
                    % (self.username, methodname, cur_nodename, self.name))

        elif kw.get("fenceinst_to_remove") and kw.get("fenceinst_to_remove_method"):
            found_instance = False
            node = self.model.retrieveNodeByName(cur_nodename)
            fenceinst = kw.get("fenceinst_to_remove")
            methodname = kw.get("fenceinst_to_remove_method")
            for child in node.getFenceNode().getChildren():
                if child.getName() == methodname:
                    node.removeFenceInstance(child, child.children[int(fenceinst) - 1])
                    found_instance = True
            if found_instance is True:
                log.info('User "%s" removed fence instance "%s" from method "%s" from node "%s" in cluster "%s"'
                    % (self.username, fenceinst, methodname, cur_nodename, self.name))
                rh.update_cluster_conf(self.model)
            else:
                log.error('User "%s" failed to remove fence instance "%s" from method "%s" from node "%s" in cluster "%s"'
                    % (self.username, fenceinst, methodname, cur_nodename, self.name))

        elif kw.get("moveup_method"):
            node = self.model.retrieveNodeByName(cur_nodename)
            methodname = kw.get("moveup_method")
            fence_elem = node.getFenceNode()
            if fence_elem is not None:
                mposition = fence_elem.findMethod(methodname)
                if mposition is not None and mposition > 0:
                    fence_elem.moveMethodUp(mposition)
                    rh.update_cluster_conf(self.model)
                    log.info('User "%s" moved up fence method "%s" for node "%s" in cluster "%s"'
                        % (self.username, methodname, cur_nodename, self.name))

        elif kw.get("movedown_method"):
            node = self.model.retrieveNodeByName(cur_nodename)
            methodname = kw.get("movedown_method")
            fence_elem = node.getFenceNode()
            levels = node.getFenceMethods()
            if fence_elem is not None:
                mposition = fence_elem.findMethod(methodname)
                if mposition is not None and mposition < len(levels) - 1:
                    fence_elem.moveMethodDown(mposition)
                    rh.update_cluster_conf(self.model)
                    log.info('User "%s" moved down fence method "%s" for node "%s" in cluster "%s"'
                        % (self.username, methodname, cur_nodename, self.name))

        elif command == "AddFence":
            node = self.model.retrieveNodeByName(cur_nodename)
            levels = node.getFenceMethods()
            fence_method = Method()
            fence_method.addAttribute('name', '1')
            if len(levels) > 0:
                methodname = kw.get('methodname')
                fence_methods = node.getFenceMethods()
                for i in fence_methods:
                    if i.getAttribute("name") == methodname:
                        fence_method = i
                        break

            parent_fencedev = kw.get('parent_fencedev').replace('fd_', '', 1)

            retcode, retobj, retunfence = validate_fenceinstance(parent_fencedev, kw.get('fence_type'), **kw)
            if retcode is True:
                # Add unfence section if requested.
                if retunfence is not None:
                    unfence = None
                    for child in node.getChildren():
                        if child.getTagName() == 'unfence':
                            unfence = child
                            break
                    if unfence is None:
                        unfence = Unfence()
                        node.addChild(unfence)
                    unfence.addChild(retunfence)
                # ---
                fence_method.addChild(retobj)
                if len(levels) == 0:
                    fence_node = node.getFenceNode()
                    fence_node.addChild(fence_method)

                flash(_('Updating fence settings for node "%s"' % cur_nodename))
                log.info('User "%s" added a fence instance to fence method "%s" for node "%s" in cluster "%s"'
                    % (self.username, methodname, cur_nodename, self.name))
                rh.update_cluster_conf(self.model)
            else:
                msgs = retobj
                if msgs and len(msgs) > 0:
                    err_msg_str = ', '.join(msgs)
                    flash('%s' % err_msg_str, status="error")
                    log.error('User "%s" failed to add a fence instance to fence method "%s" for node "%s" in cluster "%s": %s'
                        % (self.username, methodname, cur_nodename, self.name, err_msg_str))

        elif command == "EditFence":
            node = self.model.retrieveNodeByName(cur_nodename)
            instance_id = kw.get("instance_id")
            (method_num, sep, fence_instance_id) = instance_id.partition('-')

            # Create the fence device, and if it succeeds replace the old one with the new one
            retcode, retobj, retunfence = validate_fenceinstance(kw.get('fencedev'), kw.get('fence_type'), **kw)
            if retcode is True:
                # Add 'unfence' section if requested, remove it otherwise.
                old_device = node.getFenceNode().children[int(method_num)].children[int(fence_instance_id)]
                unfence = None
                unfence_handled = False
                for child in node.getChildren():
                    if child.getTagName() == 'unfence':
                        unfence = child
                        for child_device in unfence.getChildren():
                            # Try to find existing unfence device that mirrored old fence device instance
                            # (i.e. before the change, with original values of attributes) and remove it
                            # or replace it with current attributes (i.e. after the change).
                            if len(set(old_device.getAttributes().items()).difference(child_device.getAttributes().items())) == 0:
                                if (retunfence is None):
                                    unfence.removeChild(child_device)
                                    if len(unfence.getChildren()) == 0:
                                        # Remove the whole 'unfence' section from within 'node' section
                                        # it is empty.
                                        node.removeChild(unfence)
                                else:
                                    unfence.replaceChild(child_device, retunfence)
                                unfence_handled = True
                                break
                        break
                if not unfence_handled and retunfence is not None:
                    if unfence is None:
                        unfence = Unfence()
                        node.addChild(unfence)
                    unfence.addChild(retunfence)
                # ---
                node.getFenceNode().children[int(method_num)].children[int(fence_instance_id)] = retobj
                log.info('User "%s" edited "%s" fence instance of fence method "%s" for node "%s" in cluster "%s"'
                    % (self.username, kw.get('fencedev'), method_num, cur_nodename, self.name))
                rh.update_cluster_conf(self.model)

        elif command == "AddFenceMethod":
            node = self.model.retrieveNodeByName(cur_nodename)
            methodname = kw.get("newmethodname")
            method = Method()
            method.addAttribute("name", methodname)
            node.getFenceNode().addChild(method)
            log.info('User "%s" added fence method "%s" to node "%s" in cluster "%s"'
                % (self.username, methodname, cur_nodename, self.name))
            rh.update_cluster_conf(self.model)

        redirect('%s%s' % (tmpl_context.cluster_url, cur_nodename))

    # This processes all of the commands that we can apply to a node
    @expose("luci.templates.node")
    def nodes_cmd(self, command=None, **kw):
        self.get_model()
        if not self.model:
            flash(_('Unable to contact any nodes in this cluster'),
                status="error")
            redirect(tmpl_context.cluster_url)

        cur_list = []
        if 'MultiAction' in kw:
            kw["name"] = ""
            command = kw['MultiAction']
            cur_list = [x for x in kw if kw[x] == 'on' in kw[x]]
        else:
            obj_name = kw.get('name')
            if obj_name:
                cur_list = [ obj_name ]
        if len(cur_list) < 1:
            flash(_('No nodes were selected'),
                status='error')
            redirect(tmpl_context.cluster_url)

        if command == 'Reboot':
            try:
                permission_node_cmd(self.name)
            except NotAuthorizedError, e:
                flash(e, status="warning")
                redirect(tmpl_context.cluster_url)

            log.info('User "%s" rebooted "%s" in cluster "%s"'
                % (self.username, ', '.join(cur_list), self.name))
            flash(_("Rebooting %s") % ', '.join(cur_list),
                status='info')
            rh.cluster_node_reboot(self.name, cur_list)
        elif command == 'Join Cluster':
            try:
                permission_node_cmd(self.name)
            except NotAuthorizedError, e:
                flash(e, status="warning")
                redirect(tmpl_context.cluster_url)

            log.info('User "%s" started nodes "%s" in cluster "%s"'
                % (self.username, ', '.join(cur_list), self.name))
            flash(_("Starting nodes: %s") % ', '.join(cur_list),
                status='info')
            rh.cluster_node_start(self.name, cur_list)
        elif command == 'Leave Cluster':
            try:
                permission_node_cmd(self.name)
            except NotAuthorizedError, e:
                flash(e, status="warning")
                redirect(tmpl_context.cluster_url)

            log.info('User "%s" stopped nodes "%s" in cluster "%s"'
                % (self.username, ', '.join(cur_list), self.name))
            flash(_("Stopping nodes: %s") % ', '.join(cur_list),
                status='info')
            rh.cluster_node_stop(self.name, cur_list)
        elif command == 'Delete':
            try:
                permission_membership(self.name)
            except NotAuthorizedError, e:
                flash(e, status="warning")
                redirect(tmpl_context.cluster_url)

            if len(cur_list) == len(self.model.getNodes()):
                log.info('User "%s" deleted cluster "%s"'
                    % (self.username, self.name))
                flash(_("Deleting cluster: %s") % self.name, status='info')
                if rh.cluster_delete(self.name) is True:
                    redirect('/cluster/%s' % self.name)
            else:
                unstopped_nodes = False
                cstatus = self.get_status()
                if cstatus:
                    for node in cur_list:
                        nstatus = cstatus.getNodeStatus(node)
                        if nstatus.clustered == 'true':
                            unstopped_nodes = True
                if unstopped_nodes is False:
                    log.info('User "%s" deleted nodes "%s" from cluster "%s"'
                        % (self.username, ', '.join(cur_list), self.name))
                    flash(_("Deleting nodes: %s") % ', '.join(cur_list),
                        status='info')
                    rh.cluster_node_delete(self.name, self.model, cur_list)
                else:
                    flash(_("Nodes must be stopped prior to being deleted"),
                        status='error')
        elif command == 'Update Attributes':
            try:
                permission_config(self.name)
            except NotAuthorizedError, e:
                flash(e, status="warning")
                redirect(tmpl_context.cluster_url)

            vret = vcp.validate_node_prop_settings_form(cur_list[0], self.model, **kw)
            if vret[0] is True:
                log.info('User "%s" changed properties for node "%s" from cluster "%s"'
                    % (self.username, cur_list[0], self.name))

                msgs = vret[1].get('warnings')
                if msgs and len(msgs) > 0:
                    flash2.warning(', '.join(msgs))
                flash2.info(_('Updating properties of node: %s') % cur_list[0])
                flash2.flush()
                rh.update_cluster_conf(self.model)
            else:
                msgs = vret[1].get('errors')
                if msgs and len(msgs) > 0:
                    flash2.error(', '.join(msgs))
                    flash2.flush()
        else:
            log.error('User "%s" submitted unknown command "%s" for nodes "%s" from cluster "%s"' % (self.username, command, ', '.join(cur_list), self.name))
            flash(_('An unknown command "%s" was given for nodes "%s"')
                    % (command, ', '.join(cur_list)),
                status='error')
        redirect(tmpl_context.cluster_url + kw.get('name'))

    @expose("luci.templates.resource")
    def resources(self, *args):
        try:
            permission_view(self.name)
        except NotAuthorizedError, e:
            flash(e, status="warning")
            redirect("/")
 
        base_url = '/cluster/%s/resources' % self.name
        resources_cmd = '/cluster/%s/resources_cmd' % self.name

        if (len(args) >= 1):
            resourcename = '/'.join(args)
        else:
            resourcename = None
        return dict(page='nodes', name=resourcename, base_url=base_url, resources_cmd=resources_cmd)

    @expose("luci.templates.resource")
    def resources_cmd(self, command=None, **kw):
        tmpl_context.cluster_url = '/cluster/%s/resources' % self.name

        try:
            permission_config(self.name)
        except NotAuthorizedError, e:
            flash(e, status="warning")
            redirect(tmpl_context.cluster_url)
 
        self.get_model()
        if not self.model:
            flash(_('Unable to contact any nodes in this cluster'),
                status="error")
            redirect(tmpl_context.cluster_url)

        cur_list = []
        if 'MultiAction' in kw:
            kw["name"] = ""
            command = kw['MultiAction']
            cur_list = [x for x in kw if kw[x] == 'on' in kw[x]]
        else:
            obj_name = kw.get('name')
            if obj_name:
                cur_list = [ obj_name ]

        if len(cur_list) < 1 and command not in ('Create', 'Edit'):
            flash(_('No resources were selected'),
                status='error')
            redirect(tmpl_context.cluster_url)
        if command == 'Delete':
            errors = []
            res_ptr = self.model.getResourcesPtr()
            for i in cur_list:
                try:
                    cur_res = self.model.getResourceByName(i)
                    if cur_res.getRefcount() > 1:
                        errors.append(_('Global resource "%s" is in use so cannot be removed') % i)
                    else:
                        res_ptr.removeChild(cur_res)
                except:
                    pass
            if len(errors) != 0:
                flash(_('%s') % ', '.join(errors), status='error')
            else:
                log.info('User "%s" deleted resource "%s" in cluster "%s"'
                    % (self.username, ', '.join(cur_list), self.name))
                flash(_("Deleting resources %s") % ', '.join(cur_list),
                    status='info')

                rh.update_cluster_conf(self.model)
        elif command in ("Create", "Edit"):
            if command == 'Create':
                cur_action = _('Created')
            else:
                cur_action = _('Edited')
            res_type = kw.get('type', '')
            if res_type == 'ip':
                # The whole address parameter has to be constructed
                # from its parts ('address_nominal', 'address_mask') first.
                address = kw.get('address_nominal', '').strip()
                if len(kw.get('address_mask', '')) > 0:
                    mask = kw.get('address_mask', '').strip()
                    if not mask.startswith('/'):
                        address += '/'
                    address += mask
                kw['address'] = address
                kw.pop('address_nominal', None)
                kw.pop('address_mask', None)
            vret = validate_resource_form(self.model, **kw)
            if vret[0] is True:
                # For IP resources there is no name, just an IP Address
                # and to make IP addresses work you need to add a .html
                if res_type == 'ip':
                    res_name = kw.get('address')
                    redir_fmt = '%s/%s.html'
                else:
                    res_name = kw.get('resourcename')
                    redir_fmt = '%s/%s'
                log.info('User "%s" %s global resource "%s" in cluster "%s"'
                    % (self.username, cur_action, res_name, self.name))
                flash(_('%s global resource "%s"') % (cur_action, res_name))
                rh.update_cluster_conf(self.model)
                redirect(redir_fmt % (tmpl_context.cluster_url, res_name))
            else:
                msgs = vret[1].get('errors')
                if msgs and len(msgs) > 0:
                    flash(', '.join(msgs), status="error")
            redirect(tmpl_context.cluster_url)
        else:
            log.error('User "%s" submitted unknown command "%s" for resource "%s" from cluster "%s"' % (self.username, command, ', '.join(cur_list), self.name))
            flash(_('An unknown command "%s" was given for resources "%s"')
                % (command, ', '.join(cur_list)),
                    status='error')
        redirect(tmpl_context.cluster_url)

    @expose("luci.templates.service")
    def services(self, *args):
        try:
            permission_view(self.name)
        except NotAuthorizedError, e:
            flash(e, status="warning")
            redirect("/")
 
        base_url = '/cluster/%s/services' % self.name
        services_cmd = '/cluster/%s/services_cmd' % self.name

        if len(args) == 1:
            if request.response_ext:
                servicename = '%s%s' % (args[0], request.response_ext)
            else:
                servicename = args[0]
        else:
            servicename = None
        return dict(page='nodes', name=servicename, base_url=base_url, services_cmd=services_cmd)

    @expose("luci.templates.service")
    def services_cmd(self, command=None, **kw):
        tmpl_context.cluster_url = '/cluster/%s/services' % self.name

        try:
            permission_view(self.name)
        except NotAuthorizedError, e:
            flash(e, status="warning")
            redirect("/")
 
        self.get_model()
        if not self.model:
            flash(_('Unable to contact any nodes in this cluster'),
                status="error")
            redirect(tmpl_context.cluster_url)

        preferred_node = kw.get('preferred_node')

        cur_list = []
        if 'MultiAction' in kw:
            kw["name"] = ""
            command = kw['MultiAction']
            cur_list = [x for x in kw if kw[x] == 'on' in kw[x]]
        else:
            obj_name = kw.get('name')
            if obj_name:
                cur_list = [ obj_name ]

        if len(cur_list) < 1 and command not in ('Create', 'Edit'):
            flash(_('No services were selected'),
                status='error')
            redirect(tmpl_context.cluster_url)

        if command == 'Delete':
            try:
                permission_config(self.name)
            except NotAuthorizedError, e:
                flash(e, status="warning")
                redirect("/")

            log.info('User "%s" deleted service "%s" in cluster "%s"'
                % (self.username, ', '.join(cur_list), self.name))
            flash(_("Deleting services %s") % ', '.join(cur_list),
                status='info')
            for i in cur_list:
                self.model.deleteService(i)

            rh.update_cluster_conf(self.model)
            redirect(tmpl_context.cluster_url)
        if command == 'Start':
            try:
                permission_svc_cmd(self.name)
            except NotAuthorizedError, e:
                flash(e, status="warning")
                redirect("/")

            move_action = kw.get('move_action')
            if move_action == 'migrate':
                vm_name = cur_list[0]
                if not preferred_node:
                    flash(_('No destination node was given for the migration of VM "%s"') % vm_name, status="error")
                    redirect(tmpl_context.cluster_url)
                log.info('User "%s" migrated VM "%s" in cluster "%s to node %s"'
                    % (self.username, vm_name, self.name, preferred_node))
                flash(_('Migrating VM "%s" to node "%s"') % (vm_name, preferred_node))
                rh.cluster_svc_migrate(self.name, vm_name, preferred_node)
            else:
                if preferred_node:
                    node_addendum = _(" on node %s") % preferred_node
                else:
                    node_addendum = ''

                log.info('User "%s" started service "%s"%s in cluster "%s"'
                    % (self.username, ', '.join(cur_list), node_addendum, self.name))
                flash(_("Starting services %s%s") % (', '.join(cur_list), node_addendum), status='info')
                for i in cur_list:
                    rh.cluster_svc_start(self.name, i, preferred_node)
        elif command == 'Disable':
            try:
                permission_svc_cmd(self.name)
            except NotAuthorizedError, e:
                flash(e, status="warning")
                redirect("/")

            log.info('User "%s" disabled service "%s" in cluster "%s"'
                % (self.username, ', '.join(cur_list), self.name))
            flash(_("Disabling services %s") % ', '.join(cur_list),
                status='info')
            for i in cur_list:
                rh.cluster_svc_disable(self.name, i)
        elif command == 'Restart':
            try:
                permission_svc_cmd(self.name)
            except NotAuthorizedError, e:
                flash(e, status="warning")
                redirect("/")

            log.info('User "%s" restarted service "%s" in cluster "%s"'
                % (self.username, ', '.join(cur_list), self.name))
            flash(_("Restarting services %s") % ', '.join(cur_list),
                status='info')
            for i in cur_list:
                rh.cluster_svc_restart(self.name, i)
        elif command in ('Create', 'Edit'):
            try:
                permission_config(self.name)
            except NotAuthorizedError, e:
                flash(e, status="warning")
                redirect("/")

            if command == 'Create':
                cur_action = _('Created')
            else:
                cur_action = _('Edited')
            vret = validate_clusvc_form(self.model, **kw)
            kw['name'] = ''
            svc_name = kw.get('svc_name')
            if vret[0] is True:
                log.info('User "%s" %s cluster service "%s" in cluster "%s"'
                    % (self.username, cur_action, svc_name, self.name))
                flash(_('%s cluster service "%s"') % (cur_action, svc_name))
                rh.update_cluster_conf(self.model)
            else:
                msgs = vret[1].get('errors')
                if msgs and len(msgs) > 0:
                    flash(', '.join(msgs), status="error")
            redirect('%s/%s' % (tmpl_context.cluster_url, svc_name))
        else:
            log.error('User "%s" submitted unknown command "%s" for service "%s" from cluster "%s"' % (self.username, command, ', '.join(cur_list), self.name))
            flash(_('An unknown command "%s" was given for services "%s"')
                    % (command, ', '.join(cur_list)),
                status='error')
        if len(cur_list) != 1:
            redirect(tmpl_context.cluster_url)
        else:
            redirect(tmpl_context.cluster_url + '/' + cur_list[0])

    @expose("luci.templates.failover")
    def failovers(self, *args):
        failovers_cmd = '/cluster/%s/failovers_cmd' % self.name

        try:
            permission_view(self.name)
        except NotAuthorizedError, e:
            flash(e, status="warning")
            redirect("/")
 
        if len(args) == 1:
            if request.response_ext:
                failovername = '%s%s' % (args[0], request.response_ext)
            else:
                failovername = args[0]
        else:
            failovername = None
        return dict(page='nodes', name=failovername, base_url = '/cluster/' + self.name + '/failovers', failovers_cmd=failovers_cmd)

    @expose("luci.templates.failover")
    def failovers_cmd(self, command=None, **kw):
        tmpl_context.cluster_url = '/cluster/%s/failovers' % self.name

        try:
            permission_config(self.name)
        except NotAuthorizedError, e:
            flash(e, status="warning")
            redirect(tmpl_context.cluster_url)
 
        self.get_model()
        if not self.model:
            flash(_('Unable to contact any nodes in this cluster'),
                status="error")
            redirect(tmpl_context.cluster_url)

        cur_list = []
        if 'MultiAction' in kw:
            kw["name"] = ""
            command = kw['MultiAction']
            cur_list = [x for x in kw if kw[x] == 'on' in kw[x]]
        else:
            obj_name = kw.get('name')
            if obj_name:
                cur_list = [ obj_name ]

        if len(cur_list) < 1 and command != 'create':
            flash(_('No failover domains were selected'),
                status='error')
            redirect(tmpl_context.cluster_url)

        if command == 'Delete':
            log.info('User "%s" deleted failover domains "%s" in cluster "%s"'
                % (self.username, ', '.join(cur_list), self.name))
            flash(_('Deleting failover domains %s') % ', '.join(cur_list))
            for i in cur_list:
                self.model.deleteFailoverDomain(i)
            rh.update_cluster_conf(self.model)

            redirect(tmpl_context.cluster_url)

        # Delete is the only command that can be applied to multiple
        # failover domains
        if len(cur_list) > 1:
            flash(_('The settings of exactly one failover domain may be updated at one time'),
                status='error')
            redirect(tmpl_context.cluster_url)

        if command == 'update_settings':
            vret = vcp.validate_fdom_prop_settings_form(self.model, **kw)
            if vret[0] is True:
                log.info('User "%s" updated the settings of failover domain "%s" in cluster "%s"'
                    % (self.username, cur_list[0], self.name))
                flash(_('Updating settings for failover domain "%s"') % cur_list[0])
                rh.update_cluster_conf(self.model)
            else:
                msgs = vret[1].get('errors')
                if msgs and len(msgs) > 0:
                    flash(', '.join(msgs), status="error")
            redirect(tmpl_context.cluster_url + '/' + kw.get('name'))
        elif command == 'update_properties':
            vret = vcp.validate_fdom_prop_form(self.model, **kw)
            if vret[0] is True:
                log.info('User "%s" updated the properties of failover domain "%s" in cluster "%s"'
                    % (self.username, cur_list[0], self.name))
                flash(_('Updating properties for failover domain "%s"') % cur_list[0])
                rh.update_cluster_conf(self.model)
            else:
                msgs = vret[1].get('errors')
                if msgs and len(msgs) > 0:
                    flash(', '.join(msgs), status="error")
            redirect(tmpl_context.cluster_url + '/' + kw.get('name'))
        elif command == 'create':
            vret = vcp.validate_fdom_create_form(self.model, **kw)
            if vret[0] is True:
                log.info('User "%s" created failover domain "%s" in cluster "%s"'
                    % (self.username, kw.get('fdom_name'), self.name))
                flash(_('Creating failover domain "%s"') % kw.get('fdom_name'))

                rh.update_cluster_conf(self.model)
            else:
                msgs = vret[1].get('errors')
                if msgs and len(msgs) > 0:
                    flash(', '.join(msgs), status="error")
            redirect(tmpl_context.cluster_url)
        else:
            log.error('User "%s" submitted unknown command "%s" for failover domains "%s" from cluster "%s"'
                % (self.username, command, ', '.join(cur_list), self.name))
            flash(_('An unknown command "%s" was given for failover domains "%s"')
                    % (command, ', '.join(cur_list)),
                status='error')
        redirect(tmpl_context.cluster_url)

    @expose("luci.templates.fence")
    def fences(self, *args):
        fences_cmd = '/cluster/%s/fences_cmd' % self.name

        try:
            permission_view(self.name)
        except NotAuthorizedError, e:
            flash(e, status="warning")
            redirect("/")
 
        if len(args) == 1:
            if request.response_ext:
                fencename = '%s%s' % (args[0], request.response_ext)
            else:
                fencename = args[0]
        else:
            fencename = None
        return dict(page='nodes', name=fencename, base_url='/cluster/' + self.name + '/fences', fences_cmd=fences_cmd)

    @expose("luci.templates.fence")
    def fences_cmd(self, command=None, **kw):
        tmpl_context.cluster_url = '/cluster/%s/fences' % self.name

        try:
            permission_config(self.name)
        except NotAuthorizedError, e:
            flash(e, status="warning")
            redirect(tmpl_context.cluster_url)
 
        self.get_model()
        if not self.model:
            flash(_('Unable to contact any nodes in this cluster'),
                status="error")
            redirect(tmpl_context.cluster_url)

        cur_list = []
        if 'MultiAction' in kw:
            kw["name"] = ""
            command = kw['MultiAction']
            cur_list = [x for x in kw if kw[x] == 'on' in kw[x]]
        else:
            obj_name = kw.get('name')
            if obj_name:
                cur_list = [ obj_name ]

        if len(cur_list) < 1:
            flash(_('No fence devices were selected'),
                status='error')
            redirect(tmpl_context.cluster_url)

        if command == 'Create':
            fret = validateNewFenceDevice(self.model, **kw)
            if fret[0] is True:
                rh.update_cluster_conf(self.model)
                log.info('User "%s" created fence devices "%s" in cluster "%s"'
                    % (self.username, ', '.join(cur_list), self.name))
            else:
                msgs = fret[1]
                if msgs and len(msgs) > 0:
                    flash(', '.join(msgs), status="error")
        elif command == 'Delete':
            log.info('User "%s" deleted fence devices "%s" in cluster "%s"'
                % (self.username, ', '.join(cur_list), self.name))
            flash(_('Deleting fence devices ') + ', '.join(cur_list))
            updated = False
            for i in cur_list:
                cur_fencedev = self.model.getFenceDeviceByName(i)
                if not cur_fencedev:
                    continue
                updated |= self.model.deleteFenceDevice(cur_fencedev)
            if updated:
                rh.update_cluster_conf(self.model)
        elif command == 'Update':
            fret = validateFenceDevice(self.model, **kw)
            if fret[0] is True:
                rh.update_cluster_conf(self.model)
                log.info('User "%s" updated fence device "%s" in cluster "%s"'
                    % (self.username, ', '.join(cur_list), self.name))
            else:
                msgs = fret[1]
                if msgs and len(msgs) > 0:
                    flash(', '.join(msgs), status="error")
        else:
            log.error('User "%s" submitted unknown command "%s" for fence devices "%s" from cluster "%s"'
                % (self.username, command, ', '.join(cur_list), self.name))
            flash(_('An unknown command "%s" was given for fence devices "%s"')
                    % (command, ', '.join(cur_list)),
                status='error')
        redirect(tmpl_context.cluster_url)

    @expose("luci.templates.configure")
    def configure(self, *args):
        try:
            permission_view(self.name)
        except NotAuthorizedError, e:
            flash(e, status="warning")
            redirect("/")
 
        configure_cmd = '/cluster/%s/configure_cmd' % self.name
        return dict(use_referrer=False, page='nodes', name='configure', base_url='/cluster/' + self.name + '/configure', configure_cmd=configure_cmd)

    @expose("luci.templates.configure")
    def configure_cmd(self, command=None, *args, **kw):
        tmpl_context.cluster_url = '/cluster/%s/configure' % self.name

        try:
            permission_config(self.name)
        except NotAuthorizedError, e:
            flash(e, status="warning")
            redirect(tmpl_context.cluster_url)
 
        self.get_model()
        if not self.model:
            flash(_('Unable to contact any nodes in this cluster'),
                status="error")
            redirect(tmpl_context.cluster_url)

        vret = vcp.validate_cluster_config_form(self.model, **kw)
        if vret[0] is True:
            log.info('User "%s" updated the cluster properties for cluster "%s"'
                    % (self.username, self.name))
            flash("Applying Settings")
            msgs = vret[1].get('flash')
            if msgs and len(msgs) > 0:
                flash(', '.join(msgs), status="info")
            rh.update_cluster_conf(self.model)
            if vret[1].get('start_qdisk'):
                log.info('Starting qdiskd for cluster "%s"' % self.name)
                rh.cluster_node_start(self.name, [])
        else:
            msgs = vret[1].get('errors')
            if msgs and len(msgs) > 0:
                flash(', '.join(msgs), status="error")
        redirect(tmpl_context.cluster_url)

    @expose()
    def lookup(self, nodename, *args):
        try:
            permission_view(self.name)
        except NotAuthorizedError, e:
            flash(e, status="warning")
            redirect("/")
 
        inc = IndividualNodeController(self.name, self.data, unquote_plus(nodename))
        return inc, args

class IndividualNodeController(BaseController):
    def __init__(self, name, iccdata, nodename):
      self.name = name
      self.data = iccdata
      self.nodename = nodename
      tmpl_context.show_sidebar = True

    @expose("luci.templates.node")
    def index(self):
        db = get_cluster_db_obj(self.name)
        return dict(page='nodes', name=self.nodename, base_url='/nodes', nodes=db.nodes)

    @expose()
    def lookup(self, nodename, *args):
        icc = IndividualClusterController(self.name, self.data, unquote_plus(nodename))
        return icc, args
