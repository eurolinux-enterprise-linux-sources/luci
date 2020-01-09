# Copyright (C) 2009-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from luci.lib.ClusterConf.Ip import Ip
from luci.lib.ClusterConf.Fs import Fs
from luci.lib.ClusterConf.BaseResource import BaseResource
from luci.lib.ClusterConf.Clusterfs import Clusterfs
from luci.lib.ClusterConf.Netfs import Netfs
from luci.lib.ClusterConf.NFSExport import NFSExport
from luci.lib.ClusterConf.NFSClient import NFSClient
from luci.lib.ClusterConf.NFSServer import NFSServer
from luci.lib.ClusterConf.Script import Script
from luci.lib.ClusterConf.Samba import Samba
from luci.lib.ClusterConf.Smb import Smb
from luci.lib.ClusterConf.Tomcat5 import Tomcat5
from luci.lib.ClusterConf.Tomcat6 import Tomcat6
from luci.lib.ClusterConf.Postgres8 import Postgres8
from luci.lib.ClusterConf.Apache import Apache
from luci.lib.ClusterConf.OpenLDAP import OpenLDAP
from luci.lib.ClusterConf.LVM import LVM
from luci.lib.ClusterConf.MySQL import MySQL
from luci.lib.ClusterConf.DRBD import DRBD
from luci.lib.ClusterConf.Vm import Vm
from luci.lib.ClusterConf.Named import Named
from luci.lib.ClusterConf.SAPDatabase import SAPDatabase
from luci.lib.ClusterConf.SAPInstance import SAPInstance
from luci.lib.ClusterConf.OracleDB import OracleDB
from luci.lib.ClusterConf.SybaseASE import SybaseASE
from luci.lib.ClusterConf.Service import Service
from luci.lib.ClusterConf.RefObject import RefObject
from luci.lib.ClusterConf.OracleInstance import OracleInstance
from luci.lib.ClusterConf.OracleListener import OracleListener

from luci.lib.helpers import ugettext as _
from xml.dom import minidom

import logging
log = logging.getLogger(__name__)

def get_fsid_list(model):
	obj_list = model.searchObjectTree('fs')
	obj_list.extend(model.searchObjectTree('clusterfs'))
	return map(lambda x: x.getAttribute('fsid') and int(x.getAttribute('fsid')) or 0, obj_list)

def fsid_is_unique(model, fsid):
	fsid_list = get_fsid_list(model)
	return fsid not in fsid_list

def generate_fsid(model, name):
	import binascii
	from random import random
	fsid_list = get_fsid_list(model)

	fsid = binascii.crc32(name) & 0xffff
	dupe = fsid in fsid_list
	while dupe is True:
		fsid = (fsid + random.randrange(1, 0xfffe)) & 0xffff
		dupe = fsid in fsid_list
	return fsid

def getResourceForEdit(model, name):
	resPtr = model.getResourcesPtr()
	resources = resPtr.getChildren()

	for res in resources:
		if res.getName() == name:
			resPtr.removeChild(res)
			return res
	raise KeyError, name

def config_resource(params, res, rname, **kw):
	errors = list()

	for i in params:
		# parameter (str), short desc (str), required (bool), default (str or None)
		name = i[0]
		val = kw.get(name)
		required = i[2]
		default_val = i[3]

		try:
			val = val.strip()
			if not val:
				val = None
		except:
			val = None

		if not val:
			if required is True:
				if default_val is None:
					errors.append(_('No value for required attribute "%s" was given for %s resource %s') % (name, i[1], rname))
				else:
					res.addAttribute(name, default_val)
			else:
				try:
					res.removeAttribute(name)
				except:
					pass
		else:
			res.addAttribute(name, val)
	return errors

def addIp(res, rname, model, **kw):
	params = (
		('address', _('IP address'), True, None),
		('monitor_link', _('Monitor Link'), False, None),
		('disable_rdisc', _('Disable updates to static routes'), False, None),
		('sleeptime', _('Sleep time'), False, None)
	)
	if not kw.has_key('monitor_link'):
		kw['monitor_link'] = '0'
	else:
		kw['monitor_link'] = '1'
	errors = config_resource(params, res, rname, **kw)
	if res.getBinaryAttribute('monitor_link') is True:
		res.removeAttribute('monitor_link')
	return errors

def addFs(res, rname, model, **kw):
	params = (
		('mountpoint', _('Mountpoint'), True, None),
		('device', _('Device, label, or UUID'), True, None),
		('fstype', '', False, None),
		('force_unmount', '', False, None),
		('quick_status', '', False, None),
		('self_fence', '', False, None),
		('fsid', '', False, None),
		('force_fsck', '', False, None),
		('options', '', False, None)
	)
	errors = config_resource(params, res, rname, **kw)
	fsid = res.getAttribute('fsid')
	if not fsid:
		fsid = str(generate_fsid(model, rname))
		res.addAttribute('fsid', fsid)
	else:
		if not fsid_is_unique(model, int(fsid)):
			errors.append(_('fsid for resource %s is not unique') % rname)
	return errors

def addClusterfs(res, rname, model, **kw):
	params = (
		('mountpoint', '', True, None),
		('device', '', True, None),
		('fstype', '', False, None),
		('force_unmount', '', False, None),
		('self_fence', '', False, None),
		('fsid', '', False, None),
		('options', '', False, None)
	)
	errors = config_resource(params, res, rname, **kw)
	fsid = res.getAttribute('fsid')
	if not fsid:
		fsid = str(generate_fsid(model, rname))
		res.addAttribute('fsid', fsid)
	else:
		if not fsid_is_unique(model, int(fsid)):
			errors.append(_('fsid for resource %s is not unique') % rname)
	return errors

def addNetfs(res, rname, model, **kw):
	params = (
		('mountpoint', _('Mountpoint'), True, None),
		('host', _('NFS/CIFS server host'), True, None),
		('export', _('Export name'), True, None),
		('options', '', False, None),
		('no_unmount', '', False, None),
		('force_unmount', '', False, None),
		('fstype', '', False, None)
	)

	errors = config_resource(params, res, rname, **kw)
	return errors

def addVM(res, rname, model, **kw):
	params = (
		('migration_mapping', '', False, None),
		('xmlfile', '', False, None),
		('migrate', '', False, None),
		('path', '', False, None),
		('snapshot', '', False, None),
		('hypervisor_uri', '', False, None),
		('migration_uri', '', False, None),
		('status_program', '', False, None)
	)

	errors = config_resource(params, res, rname, **kw)
	return errors

def addNFSClient(res, rname, model, **kw):
	params = (
		('target', _('Hosts to export to'), True, None),
		('options', '', False, None),
		('allow_recover', '', False, None)
	)

	errors = config_resource(params, res, rname, **kw)
	if kw.get('expert_mode'):
		# The inherited path can be overriden while in expert mode
		path_override = kw.get('path')
		if path_override and not path_override.isspace():
			res.addAttribute('path', path_override)
		else:
			res.removeAttribute('path')
	return errors

def addNFSExport(res, rname, model, **kw):
	# Only the name is used

	if kw.get('expert_mode'):
		# The inherited path can be overriden while in expert mode
		path_override = kw.get('path')
		if path_override and not path_override.isspace():
			res.addAttribute('path', path_override)
		else:
			res.removeAttribute('path')
	return []

def addNFSServer(res, rname, model, **kw):
	params = (
		('nfspath', '', False, None),
	)

	errors = config_resource(params, res, rname, **kw)
	if kw.get('expert_mode'):
		# The inherited path can be overriden while in expert mode
		path_override = kw.get('path')
		if path_override and not path_override.isspace():
			res.addAttribute('path', path_override)
		else:
			res.removeAttribute('path')
	return errors

def addScript(res, rname, model, **kw):
	params = (
		('file', _('Path to script'), True, None),
	)
	errors = config_resource(params, res, rname, **kw)
	return errors

def addSmb(res, rname, model, **kw):
	params = (
		('workgroup', '', False, None),
	)
	errors = config_resource(params, res, rname, **kw)
	return errors

def addSamba(res, rname, model, **kw):
	params = (
		('config_file', _('Path to configuration file'), False, None),
		('smbd_options', '', False, None),
		('nmbd_options', '', False, None),
		('shutdown_wait', '', False, None)
	)
	errors = config_resource(params, res, rname, **kw)
	return errors

def addApache(res, rname, model, **kw):
	params = (
		('config_file', _('Path to configuration file'), False, None),
		('server_root', '', False, None),
		('httpd_options', '', False, None),
		('shutdown_wait', '', False, None)
	)
	errors = config_resource(params, res, rname, **kw)
	return errors

def addMySQL(res, rname, model, **kw):
	params = (
		('config_file', _('Path to configuration file'), False, None),
		('listen_address', '', False, None),
		('mysqld_options', '', False, None),
		('startup_wait', '', False, None),
		('shutdown_wait', '', False, None)
	)
	errors = config_resource(params, res, rname, **kw)
	return errors

def addOpenLDAP(res, rname, model, **kw):
	params = (
		('config_file', _('Path to configuration file'), False, None),
		('url_list', '', False, None),
		('slapd_options', '', False, None),
		('shutdown_wait', '', False, None)
	)
	errors = config_resource(params, res, rname, **kw)
	return errors

def addPostgres8(res, rname, model, **kw):
	params = (
		('config_file', _('Path to configuration file'), False, None),
		('postmaster_user', '', False, None),
		('postmaster_options', '', False, None),
		('shutdown_wait', '', False, None)
	)
	errors = config_resource(params, res, rname, **kw)
	return errors

def addTomcat5(res, rname, model, **kw):
	params = (
		('config_file', _('Path to configuration file'), False, None),
		('tomcat_user', '', False, None),
		('catalina_options', '', False, None),
		('catalina_base', '', False, None),
		('shutdown_wait', '', False, None)
	)
	errors = config_resource(params, res, rname, **kw)
	return errors

def addTomcat6(res, rname, model, **kw):
	params = (
		('config_file', _('Path to configuration file'), False, None),
		('shutdown_wait', '', False, None)
	)
	errors = config_resource(params, res, rname, **kw)
	return errors

def addLVM(res, rname, model, **kw):
	params = (
		('vg_name', _('Volume group name'), True, None),
		('lv_name', '', False, None),
		('self_fence', '', False, None)
	)
	errors = config_resource(params, res, rname, **kw)
	return errors

def addSAPDatabase(res, rname, model, **kw):
	params = (
		('DBTYPE', _('Database type'), True, None),
		('DIR_EXECUTABLE', '', False, None),
		('NETSERVICENAME', '', False, None),
		('DBJ2EE_ONLY', '', False, None),
		('JAVA_HOME', '', False, None),
		('STRICT_MONITORING', '', False, None),
		('AUTOMATIC_RECOVER', '', False, None),
		('DIR_BOOTSTRAP', '', False, None),
		('DIR_SECSTORE', '', False, None),
		('DB_JARS', '', False, None),
		('PRE_START_USEREXIT', '', False, None),
		('POST_START_USEREXIT', '', False, None),
		('PRE_STOP_USEREXIT', '', False, None),
		('POST_STOP_USEREXIT', '', False, None),
	)
	errors = config_resource(params, res, rname, **kw)
	res.removeAttribute('name')
	res.addAttribute('SID', rname)

	dbtype = res.getAttribute('DBTYPE')
	if not dbtype:
		dbtype = 'ORA'
		res.addAttribute('DBTYPE', 'ORA')
	if not dbtype.upper() in ( 'ORA', 'DB6', 'ADA' ):
		errors.append(_('Invalid database type: %s') % dbtype)
	return errors

def addSAPInstance(res, rname, model, **kw):
	params = (
		('DIR_EXECUTABLE', '', False, None),
		('DIR_PROFILE', '', False, None),
		('START_PROFILE', '', False, None),
		('START_WAITTIME', '', False, None),
		('AUTOMATIC_RECOVER', '', False, None),
		('PRE_START_USEREXIT', '', False, None),
		('POST_START_USEREXIT', '', False, None),
		('PRE_STOP_USEREXIT', '', False, None),
		('POST_STOP_USEREXIT', '', False, None)
	)

	errors = config_resource(params, res, rname, **kw)
	res.removeAttribute('name')
	res.addAttribute('InstanceName', rname)
	return errors

def addSybaseASE(res, rname, model, **kw):
	params = (
		('sybase_home', _('SYBASE home directory'), True, None),
		('sybase_ase', _('SYBASE_ASE directory name'), True, None),
		('sybase_ocs', _('SYBASE_OCS directory name'), True, None),
		('server_name', _('ASE server name'), True, None),
		('login_file', _('Login file'), True, None),
		('interfaces_file', _('Interfaces file'), True, None),
		('sybase_user', _('Sybase user'), True, 'sybase'),
		('shutdown_timeout', _('Shutdown timeout value'), True, None),
		('start_timeout', _('Start timeout value'), True, None),
		('deep_probe_timeout', _('Deep probe timeout value'), True, None)
	)
	errors = config_resource(params, res, rname, **kw)
	return errors

def addOracleDB(res, rname, model, **kw):
	params = (
		('user', _('Oracle User Name'), True, None),
		('home', _('Oracle Home Directory'), True, None),
		('listener_name', '', False, None),
		('oracletype', _('Oracle Installation Type'), True, '10g'),
		('vhost', _('Virtual Hostname'), False, None)
	)
	errors = config_resource(params, res, rname, **kw)
	dbtype = res.getAttribute('oracletype')
	if not dbtype.lower() in ('base', 'base-em', 'ias', '10g', '10g-ias'):
		errors.append(_('Invalid Oracle database type "%s"') % dbtype)
	if dbtype:
		res.removeAttribute('oracletype')
		res.addAttribute('type', dbtype)
	return errors

def addOracleInstance(res, rname, model, **kw):
	params = (
		('user', _('Oracle User Name'), True, None),
		('home', _('Oracle Home Directory'), True, None),
		('listeners', _('Oracle listeners'), False, None),
		('lockfile', _('Path to lock file'), False, None),
	)
	errors = config_resource(params, res, rname, **kw)
	return errors

def addOracleListener(res, rname, model, **kw):
	params = (
		('user', _('Oracle User Name'), True, None),
		('home', _('Oracle Home Directory'), True, None),
	)
	errors = config_resource(params, res, rname, **kw)
	return errors

def addNamed(res, rname, model, **kw):
	params = (
		('config_file', _('named config file'), False, None),
		('named_working_dir', _('named working directory'), False, None),
		('named_sdb', _('named simplified database backend'), False, None),
		('named_options', _('Other command line options'), False, None),
		('shutdown_wait', _('Shutdown Wait Time'), False, None)
	)
	errors = config_resource(params, res, rname, **kw)
	return errors

def addDRBD(res, rname, model, **kw):
	params = (
		('resource', _('drbd resource name'), True, None),
	)
	errors = config_resource(params, res, rname, **kw)
	return errors

resource_table = {
	'ip':				( addIp,				Ip				),
	'fs':				( addFs,				Fs				),
	'clusterfs':		( addClusterfs,			Clusterfs		),
	'netfs':			( addNetfs,				Netfs			),
	'nfsexport':		( addNFSExport,			NFSExport		),
	'nfsclient':		( addNFSClient,			NFSClient		),
	'nfsserver':		( addNFSServer,			NFSServer		),
	'script':			( addScript,			Script			),
	'samba':			( addSamba,				Samba			),
	'smb':				( addSmb,				Smb				),
	'tomcat-5':			( addTomcat5,			Tomcat5			),
	'tomcat-6':			( addTomcat6,			Tomcat6			),
	'postgres-8':		( addPostgres8,			Postgres8		),
	'apache':			( addApache,			Apache			),
	'openldap':			( addOpenLDAP,			OpenLDAP		),
	'lvm':				( addLVM,				LVM				),
	'mysql':			( addMySQL,				MySQL			),
	'SAPDatabase':		( addSAPDatabase,		SAPDatabase		),
	'SAPInstance':		( addSAPInstance,		SAPInstance		),
	'oracledb':			( addOracleDB,			OracleDB		),
	'orainstance':		( addOracleInstance,	OracleInstance	),
	'oralistener':		( addOracleListener,	OracleListener	),
	'ASEHAagent':		( addSybaseASE,			SybaseASE		),
	'named':			( addNamed,				Named			),
	'drbd':				( addDRBD,				DRBD			),
	'vm':				( addVM,				Vm				),
}

def create_resource(res_type, model, **kw):
	errors = list()
	if not res_type:
		raise Exception, _('No resource type was given')

	if not resource_table.has_key(res_type):
		raise Exception, _('Unknown resource type: "%s"') % res_type

	res = None

	resource_edit = False
	oldname = None
	if kw.has_key('edit'):
		resource_edit = True
		try:
			if not kw.has_key('oldname'):
				raise Exception, _('Cannot find this resource\'s original name.')

			oldname = kw['oldname'].strip()
			if not oldname:
				raise Exception, _('Cannot find this resource\'s original name.')

			res = getResourceForEdit(model, oldname)
			if not res:
				raise Exception, _('Cluster model object for "%s" not found') % oldname
		except Exception, e:
			log.exception('Error adding resource: %s' % str(e))
			raise Exception, _('No resource named "%s" exists.') % oldname
	else:
		res = resource_table[res_type][1]()

	if res_type == 'ip':
		rname = kw.get('address')
	elif res_type == 'vm':
		rname = ''
		res = BaseResource()
	else:
		if not kw.has_key('resourcename') or not kw['resourcename'].strip():
			raise Exception, _('All resources must have a unique name.')
		rname = kw['resourcename'].strip()
		res.addAttribute('name', rname)

	if not resource_edit:
		try:
			dummy = getResourceForEdit(model, rname)
			if dummy:
				raise Exception, _('A resource named "%s" already exists.') % rname
		except:
			pass

	errors = resource_table[res_type][0](res, rname, model, **kw)
	if resource_edit and oldname != res.getName():
		res.updateRefName(oldname, res.getName())

	if len(errors) > 0:
		raise Exception, ', '.join(errors)

	return res

def validate_clusvc_form(model, **kw):
	errors = list()

	new_service = Service()
	old_name = kw.get('old_name')
	service_name = kw.get('svc_name')

	action = kw.get('action')
	if action is None:
		errors.append(_('No action was given for service "%s"') % service_name)
		return (False, {'errors': errors})

	action = action.lower()
	if action == 'edit':
		cur_service = model.retrieveServiceByName(old_name)
		if cur_service is None:
			errors.append(_('The service "%s" could not be found for editing') % service_name)
			return (False, {'errors': errors})
		new_service.getAttributes().update(cur_service.getAttributes())
		model.deleteService(old_name)
	elif action == 'create':
		cur_service = model.retrieveServiceByName(service_name)
		if cur_service is not None:
			errors.append(_('A cluster service with the name "%s" already exists') % service_name)
			return (False, {'errors': errors})
	else:
		errors.append(_('An unknown action "%s" was specified') % action)
		return (False, {'errors': errors})

	if not service_name or service_name.isspace():
		errors.append(_('No service name was given'))
		return (False, {'errors': errors})
	new_service.setName(service_name)

	recovery = kw.get('recovery')
	try:
		new_service.setRecoveryPolicy(recovery)
	except:
		errors.append(_('Invalid recovery policy: %s') % recovery)

	if new_service.getRecoveryPolicy() in ('restart', 'restart-disable'):
		max_restarts = kw.get('max_restarts')
		if max_restarts and not max_restarts.isspace():
			try:
				new_service.setMaxRestarts(max_restarts)
			except:
				errors.append(_('Maximum restarts must be a number greater than or equal to 0'))
		else:
			new_service.delMaxRestarts()

		restart_expire_time = kw.get('restart_expire_time')
		if restart_expire_time and not restart_expire_time.isspace():
			try:
				new_service.setRestartExpireTime(restart_expire_time)
			except:
				errors.append(_('Restart expire time must be a number greater than or equal to 0'))
		else:
			new_service.delRestartExpireTime()
	else:
		new_service.delMaxRestarts()
		new_service.delRestartExpireTime()

	fdom = kw.get('domain')
	if fdom and not fdom.isspace():
		new_service.setFailoverDomain(fdom)
	else:
		new_service.delFailoverDomain()

	new_service.setAutostart(kw.get('autostart') is not None)

	# In central processing mode, exclusive is an integer. When not in
	# central processing mode, it's boolean.
	ex_val = kw.get('exclusive')
	if model.getResourceManagerPtr().getCentralProcessing() is True:
		if ex_val and not ex_val.isspace():
			try:
				new_service.setExclusive(ex_val)
			except:
				errors.append(_('Invalid value specified for the exclusive property: %s') % ex_val)
		else:
			new_service.delExclusive()
	else:
		if ex_val is not None:
			new_service.setExclusive(1)
		else:
			new_service.delExclusive()

	if kw.get('expert_mode'):
		new_service.setNFSLock(kw.get('nfslock') is not None)
		new_service.setNFSClientCache(kw.get('nfs_client_cache') is not None)

		cp_pri = kw.get('priority')
		if cp_pri and not cp_pri.isspace():
			try:
				new_service.setPriority(cp_pri)
			except:
				errors.append(_('Invalid value for priority: %s') % cp_pri)
		else:
			new_service.delPriority()

		svc_depend = kw.get('depend')
		if svc_depend and not svc_depend.isspace():
			test_name = svc_depend
			if test_name.startswith('service:'):
				test_name = test_name[8:]
			elif test_name.startswith('vm:'):
				test_name = test_name[3:]
			else:
				svc_depend = 'service:%s' % svc_depend
			
			try:
				test_svc = model.retrieveServiceByName(test_name)
				if not test_svc:
					errors.append(_('Invalid value for service dependency: %s: No such service exists') % test_name)
				else:
					new_service.setDepend(svc_depend)
			except:
				errors.append(_('Invalid value for service dependency: %s') % svc_depend)
		else:
			new_service.delDepend()

		depend_mode = kw.get('depend_mode')
		if depend_mode and not depend_mode.isspace():
			try:
				new_service.setDependMode(depend_mode)
			except:
				errors.append(_('Invalid dependency mode: %s') % depend_mode)
		else:
			new_service.delDependMode()

	form_xml = kw.get('form_xml')
	if not form_xml:
		form_xml = ''

	root_elem = kw.get('root_elem')
	if not root_elem:
		root_elem = 'svc_root'

	forms = []
	if form_xml.strip():
		try:
			doc = minidom.parseString(form_xml)
			forms = doc.getElementsByTagName('form')
		except:
			log.exception('Error parsing service XML: "%s"' % form_xml)
			return (False, { 'errors': [ _('The resource data submitted for this service is not properly formed') ]})

	is_vm = False
	form_hash = {}
	form_hash[root_elem] = { 'form': None, 'kids': [] }
	for i in forms:
		form_id = i.getAttribute('id')
		form_parent = i.getAttribute('parent')
		if not form_id or not form_parent:
			continue
		ielems = i.getElementsByTagName('input')
		if not ielems or len(ielems) < 1:
			continue
		if not form_id in form_hash:
			form_hash[form_id] = {'form': i, 'kids': []}
		elif not form_hash[form_id]['form']:
			form_hash[form_id]['form'] = i
		if not form_parent in form_hash:
			form_hash[form_parent] = {'form': None, 'kids': []}
		form_hash[form_parent]['kids'].append(form_id)
		dummy_form = {}

		for i in ielems:
			try:
				input_type = str(i.getAttribute('type'))
			except:
				log.exception('No input type')
				continue

			if not input_type or input_type == 'button':
				continue

			try:
				dummy_form[str(i.getAttribute('name'))] = str(i.getAttribute('value'))
			except:
				log.exception('Error parsing form XML values')

		try:
			res_type = dummy_form['type'].strip()
			if not res_type:
				raise Exception, 'no resource type'
			if res_type == 'vm':
				is_vm = True
		except Exception, e:
			log.exception('no resource type')
			return (False, { 'errors': [ _('No resource type was specified') ]})

		try:
			if res_type == 'ip':
				mask = dummy_form.get('address_mask')
				if mask:
					dummy_form['resourcename'] = '%s/%s' % (dummy_form['address_nominal'], dummy_form['address_mask'])
				else:
					dummy_form['resourcename'] = dummy_form['address_nominal']
				dummy_form['address'] = dummy_form['resourcename']
		except:
			log.exception('no ipaddr')
			return (False, { 'errors': [ _('No IP address was given') ]})

		try:
			if dummy_form.has_key('global'):
				newRes = model.getResourceByName(dummy_form['resourcename'])
				resObj = RefObject(newRes)
				resObj.setRef(newRes.getName())
				cur_res_name = 'resource "%s"' % dummy_form['resourcename']
			else:
				cur_res_name = "%s resource" % res_type
				resObj = create_resource(res_type, model, **dummy_form)
				if resObj:
					cur_name = resObj.getName()
					if cur_name:
						cur_res_name = 'resource "%s"' % cur_name
		except Exception, e:
			resObj = None
			errors.append(_('Error adding resource type %s: %s') % (res_type, str(e)))
			log.exception('Error validating %s resource "%r"' % (res_type, dummy_form))

		if not resObj:
			continue

		isubtree = True
		if dummy_form.has_key('expert_mode'):
			resObj.setEnforceTimeouts(dummy_form.has_key('enforce_timeouts'))
		if dummy_form.has_key('noncritical_resource'):
			resObj.setNonCriticalResource(True)
		elif dummy_form.has_key('independent_subtree'):
			resObj.setIndependentSubtree(True)
		else:
			# These do not apply if __independent_subtree is not 1 or 2
			isubtree = False
			resObj.delSubtreeProperties()

		if isubtree is True:
			max_restarts = dummy_form.get('__max_restarts')
			if max_restarts and not max_restarts.isspace():
				try:
					resObj.setResMaxRestarts(max_restarts)
				except:
					errors.append(_('Invalid value for max restarts for %s: %s') % (cur_res_name, max_restarts))
			else:
				resObj.delResMaxRestarts()
				resObj.delResRestartExpireTime()

			restart_expire_time = dummy_form.get('__restart_expire_time')
			if restart_expire_time and not restart_expire_time.isspace():
				try:
					resObj.setResRestartExpireTime(restart_expire_time)
				except:
					errors.append(_('Invalid value for restart expire time for %s: %s') % (cur_res_name, restart_expire_time))
			else:
				resObj.delResRestartExpireTime()

			max_failures = dummy_form.get('__max_failures')
			if max_failures and not max_failures.isspace():
				try:
					resObj.setMaxFailures(max_failures)
				except:
					errors.append(_('Invalid value for max failures for %s: %s') % (cur_res_name, max_failures))
			else:
				resObj.delMaxFailures()
				resObj.delFailureExpireTime()

			failure_expire_time = dummy_form.get('__failure_expire_time')
			if failure_expire_time and not failure_expire_time.isspace():
				try:
					resObj.setFailureExpireTime(failure_expire_time)
				except:
					errors.append(_('Invalid value for failure expire time for %s: %s') % (cur_res_name, failure_expire_time))
			else:
				resObj.delFailureExpireTime()

		form_hash[form_id]['obj'] = resObj

	if len(errors) > 0:
		return (False, {'errors': errors})

	def buildSvcTree(parent, child_id_list):
		for i in child_id_list:
			try:
				child = form_hash[i]['obj']
				if not child:
					raise Exception, 'No object for %s' % i
			except Exception, e:
				log.exception('Error building service tree')
				continue
			parent.addChild(child)
			if 'kids' in form_hash[i]:
				buildSvcTree(child, form_hash[i]['kids'])

	buildSvcTree(new_service, form_hash[root_elem]['kids'])

	if is_vm is True:
		svc_children = new_service.getChildren()
		if len(svc_children) != 1:
			errors.append(_('VMs can have no children and cannot be children of resources'))
		else:
			# Because we're treating vm like a resource from the point of
			# view of the user, we need to use the service level attributes
			# from "new_service" and the resource level attributes from its
			# first child
			new_vm = Vm()
			new_vm.getAttributes().update(new_service.getAttributes())
			new_vm.delResourceAttributes()

			form_vm = Vm()
			form_vm.getAttributes().update(svc_children[0].getAttributes())

			new_vm.getAttributes().update(form_vm.getResourceAttributes())
			model.resourcemanager_ptr.addChild(new_vm)
	else:
		model.resourcemanager_ptr.addChild(new_service)
	return (len(errors) == 0, {'errors': errors})

def validate_resource_form(model, **kw):
	errors = []

	try:
		res_type = kw.get('type')
		res = create_resource(res_type, model, **kw)
		model.getResourcesPtr().addChild(res)
	except Exception, e:
		errors.append(_('Error adding resource type %s: %s') % (res_type, str(e)))
		return (False, {'errors': errors})
	return (True, {})
