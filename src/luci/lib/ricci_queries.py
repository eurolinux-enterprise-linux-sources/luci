# Copyright (C) 2006-2010 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from luci.lib.helpers import ugettext as _
from xml.dom import minidom
from ricci_communicator import batch_status

class RicciQueriesError(Exception):
	pass

def addClusterNodeBatch(model,
						install_base,
						install_services,
						install_shared_storage,
						upgrade_rpms,
						reboot_nodes=False):
	batch = list()

	clusterconf = model.exportModelAsString()
	conf = clusterconf.replace('<?xml version="1.0"?>', '')
	conf = conf.replace('<?xml version="1.0" ?>', '')
	conf = conf.replace('<? xml version="1.0"?>', '')
	conf = conf.replace('<? xml version="1.0" ?>', '')

	batch.append('<module name="rpm">')
	batch.append('<request API_version="1.0">')
	batch.append('<function_call name="install">')
	if upgrade_rpms:
		batch.append('<var name="upgrade" type="boolean" value="true"/>')
	else:
		batch.append('<var name="upgrade" type="boolean" value="false"/>')
	batch.append('<var name="sets" type="list_xml">')
	if install_base or install_services or install_shared_storage:
		batch.append('<set name="Cluster Base"/>')
	if install_services:
		batch.append('<set name="Cluster Service Manager"/>')
	if install_shared_storage:
		batch.append('<set name="Clustered Storage"/>')
	batch.append('</var>')
	batch.append('</function_call>')
	batch.append('</request>')
	batch.append('</module>')

	batch.append('<module name="service">')
	batch.append('<request API_version="1.0">')
	batch.append('<function_call name="disable">')
	batch.append('<var mutable="false" name="services" type="list_xml">')
	if install_base or install_services or install_shared_storage:
		batch.append('<set name="Cluster Base"/>')
	if install_services:
		batch.append('<set name="Cluster Service Manager"/>')
	if install_shared_storage:
		batch.append('<set name="Clustered Storage"/>')
	batch.append('</var>')
	batch.append('</function_call>')
	batch.append('</request>')
	batch.append('</module>')

	need_reboot = reboot_nodes
	if need_reboot:
		batch.append('<module name="reboot">')
		batch.append('<request API_version="1.0">')
		batch.append('<function_call name="reboot_now"/>')
		batch.append('</request>')
		batch.append('</module>')
	else:
		batch.append('<module name="rpm">')
		batch.append('<request API_version="1.0">')
		batch.append('<function_call name="install"/>')
		batch.append('</request>')
		batch.append('</module>')

	batch.append('<module name="cluster">')
	batch.append('<request API_version="1.0">')
	batch.append('<function_call name="set_cluster.conf">')
	batch.append('<var mutable="false" name="propagate" type="boolean" value="false"/>')
	batch.append('<var mutable="false" name="cluster.conf" type="xml">%s</var>' % conf)
	batch.append('</function_call>')
	batch.append('</request>')
	batch.append('</module>')

	if install_shared_storage:
		batch.append('<module name="storage">')
		batch.append('<request API_version="1.0">')
		batch.append('<function_call name="enable_clustered_lvm"/>')
		batch.append('</request>')
		batch.append('</module>')
	else:
		batch.append('<module name="rpm">')
		batch.append('<request API_version="1.0">')
		batch.append('<function_call name="install"/>')
		batch.append('</request>')
		batch.append('</module>')

	batch.append('<module name="cluster">')
	batch.append('<request API_version="1.0">')
	batch.append('<function_call name="start_node">')
	batch.append('<var mutable="false" name="enable_services" type="boolean" value="true"/>')
	batch.append('</function_call>')
	batch.append('</request>')
	batch.append('</module>')

	return ''.join(batch)

def createClusterBatch( cluster_name,
						node_names,
						install_base,
						install_services,
						install_shared_storage,
						upgrade_rpms,
						reboot_nodes=False):

	batch = list()
	batch.append('<module name="rpm">')
	batch.append('<request API_version="1.0">')
	batch.append('<function_call name="install">')
	if upgrade_rpms:
		batch.append('<var name="upgrade" type="boolean" value="true"/>')
	else:
		batch.append('<var name="upgrade" type="boolean" value="false"/>')

	batch.append('<var name="sets" type="list_xml">')
	if install_base or install_services or install_shared_storage:
		batch.append('<set name="Cluster Base"/>')

	if install_services:
		batch.append('<set name="Cluster Service Manager"/>')

	if install_shared_storage:
		batch.append('<set name="Clustered Storage"/>')
	batch.append('</var>')
	batch.append('</function_call>')
	batch.append('</request>')
	batch.append('</module>')

	batch.append('<module name="service">')
	batch.append('<request API_version="1.0">')
	batch.append('<function_call name="disable">')
	batch.append('<var mutable="false" name="services" type="list_xml">')
	if install_base or install_services or install_shared_storage:
		batch.append('<set name="Cluster Base"/>')
	if install_services:
		batch.append('<set name="Cluster Service Manager"/>')
	if install_shared_storage:
		batch.append('<set name="Clustered Storage"/>')
	batch.append('</var>')
	batch.append('</function_call>')
	batch.append('</request>')
	batch.append('</module>')

	need_reboot = reboot_nodes
	if need_reboot:
		batch.append('<module name="reboot">')
		batch.append('<request API_version="1.0">')
		batch.append('<function_call name="reboot_now"/>')
		batch.append('</request>')
		batch.append('</module>')
	else:
		batch.append('<module name="rpm">')
		batch.append('<request API_version="1.0">')
		batch.append('<function_call name="install"/>')
		batch.append('</request>')
		batch.append('</module>')

	batch.append('<module name="cluster">')
	batch.append('<request API_version="1.0">')
	batch.append('<function_call name="set_cluster.conf">')
	batch.append('<var mutable="false" name="propagate" type="boolean" value="false"/>')
	batch.append('<var mutable="false" name="cluster.conf" type="xml">')
	batch.append('<cluster config_version="1" name="%s">' % cluster_name)
	batch.append('<clusternodes>')
	x = 1
	for i in node_names:
		batch.append('<clusternode name="%s" nodeid="%d"/>' % (i, x))
		x += 1
	batch.append('</clusternodes>')

	if len(node_names) == 2:
		batch.append('<cman expected_votes="1" two_node="1"/>')
	else:
		batch.append('<cman/>')
	batch.append('<fencedevices/>')
	batch.append('<rm/>')
	batch.append('</cluster>')
	batch.append('</var>')
	batch.append('</function_call>')
	batch.append('</request>')
	batch.append('</module>')

	if install_shared_storage:
		batch.append('<module name="storage">')
		batch.append('<request API_version="1.0">')
		batch.append('<function_call name="enable_clustered_lvm"/>')
		batch.append('</request>')
		batch.append('</module>')
	else:
		batch.append('<module name="rpm">')
		batch.append('<request API_version="1.0">')
		batch.append('<function_call name="install"/>')
		batch.append('</request>')
		batch.append('</module>')

	batch.append('<module name="cluster">')
	batch.append('<request API_version="1.0">')
	batch.append('<function_call name="start_node">')
	batch.append('<var mutable="false" name="cluster_startup" type="boolean" value="true"/>')
	batch.append('</function_call>')
	batch.append('</request>')
	batch.append('</module>')
	return ''.join(batch)

def batchAttemptResult(doc):
	if not doc:
		return (None, None)

	try:
		batch = doc.getElementsByTagName('batch')
		if not batch or len(batch) < 1:
			raise RicciQueriesError, 'no batch tag was found'
	except Exception, e:
		return (None, None)

	for i in batch:
		try:
			batch_number = str(i.getAttribute('batch_id'))
			result = str(i.getAttribute('status'))
			return (batch_number, result)
		except Exception, e:
			pass

	return (None, None)

def getClusterStatusBatch(rc):
	batch_str = '<module name="cluster"><request API_version="1.0"><function_call name="status"/></request></module>'
	ricci_xml = rc.batch_run(batch_str, async=False)

	if not ricci_xml:
		return None

	try:
		cluster_tags = ricci_xml.getElementsByTagName('cluster')
	except Exception, e:
		return None

	if len(cluster_tags) != 1:
		return None

	try:
		cluster_node = cluster_tags[0]
		if not cluster_node:
			raise RicciQueriesError, 'element 0 is None'
	except Exception, e:
		return None

	try:
		doc = minidom.Document()
		doc.appendChild(cluster_node)
		return doc
	except Exception, e:
		pass

	return None

def setClusterVersion(rc, version):
	batch_str = '<module name="cluster"><request API_version="1.0"><function_call name="set_cluster_version"><var type="int" name="version" mutable="false" value="%s"/></function_call></request></module>' % version
	ricci_xml = rc.batch_run(batch_str)
	return batchAttemptResult(ricci_xml)

def setClusterConf(rc, clusterconf, propagate=False):
	if propagate is True:
		propg = 'true'
	else:
		propg = 'false'

	conf = clusterconf.replace('<?xml version="1.0"?>', '')
	conf = conf.replace('<?xml version="1.0" ?>', '')
	conf = conf.replace('<? xml version="1.0"?>', '')
	conf = conf.replace('<? xml version="1.0" ?>', '')

	batch_str = '<module name="cluster"><request API_version="1.0"><function_call name="set_cluster.conf"><var type="boolean" name="propagate" mutable="false" value="%s"/><var type="xml" mutable="false" name="cluster.conf">%s</var></function_call></request></module>' % (propg, conf)

	ricci_xml = rc.batch_run(batch_str)
	return batchAttemptResult(ricci_xml)

def setClusterConfSync(rc, clusterconf, propagate=True):
	if propagate is True:
		propg = 'true'
	else:
		propg = 'false'

	conf = clusterconf.replace('<?xml version="1.0"?>', '')
	conf = conf.replace('<?xml version="1.0" ?>', '')
	conf = conf.replace('<? xml version="1.0"?>', '')
	conf = conf.replace('<? xml version="1.0" ?>', '')

	batch_str = '<module name="cluster"><request API_version="1.0"><function_call name="set_cluster.conf"><var type="boolean" name="propagate" mutable="false" value="%s"/><var type="xml" mutable="false" name="cluster.conf">%s</var></function_call></request></module>' % (propg, conf)

	ricci_xml = rc.batch_run(batch_str, async=False)
	if not ricci_xml:
		return False
	batch_xml = ricci_xml.getElementsByTagName('batch')
	if not batch_xml:
		return None
	(num, total) = batch_status(batch_xml[0])
	if num == total:
		return True
	return False

def getNodeLogs(rc):
	from time import time, ctime

	errstr = 'log not accessible'

	batch_str = '<module name="log"><request API_version="1.0"><function_call name="get"><var mutable="false" name="age" type="int" value="18000"/><var mutable="false" name="tags" type="list_str"></var></function_call></request></module>'

	ricci_xml = rc.batch_run(batch_str, async=False)
	if not ricci_xml:
		return errstr
	try:
		log_entries = ricci_xml.getElementsByTagName('logentry')
		if not log_entries or len(log_entries) < 1:
			raise RicciQueriesError, 'no log data is available.'
	except Exception, e:
		return None

	time_now = time()
	entry_list = list()

	try:
		# Show older entries first.
		log_entries.sort(lambda x, y: int(y.getAttribute('age')) - int(x.getAttribute('age')))
	except:
		pass

	for i in log_entries:
		try:
			log_msg = i.getAttribute('msg')
		except:
			log_msg = ''

		if not log_msg:
			continue

		try:
			log_age = int(i.getAttribute('age'))
		except:
			log_age = 0

		try:
			log_domain = i.getAttribute('domain')
		except:
			log_domain = ''

		try:
			log_pid = i.getAttribute('pid')
		except:
			log_pid = ''

		if log_age:
			entry_list.append('%s ' % ctime(time_now - log_age))
		if log_domain:
			entry_list.append(log_domain)
		if log_pid:
			entry_list.append('[%s]' % log_pid)
		entry_list.append(': %s<br/>' % log_msg)
	return ''.join(entry_list)

def nodeReboot(rc):
	batch_str = '<module name="reboot"><request API_version="1.0"><function_call name="reboot_now"/></request></module>'

	ricci_xml = rc.batch_run(batch_str)
	return batchAttemptResult(ricci_xml)

def nodeLeaveCluster(	rc,
						cluster_shutdown=False,
						purge=False,
						disable_services=False):
	cshutdown = 'false'
	if cluster_shutdown is True:
		cshutdown = 'true'

	purge_conf = 'false'
	if purge is True:
		purge_conf = 'true'

	disable_svc = 'false'
	if disable_services is True:
		disable_svc = 'true'

	batch_str = '<module name="cluster"><request API_version="1.0"><function_call name="stop_node"><var mutable="false" name="cluster_shutdown" type="boolean" value="%s"/><var mutable="false" name="purge_conf" type="boolean" value="%s"/><var mutable="false" name="disable_services" type="boolean" value="%s"/></function_call></request></module>' % (cshutdown, purge_conf, disable_svc)

	ricci_xml = rc.batch_run(batch_str)
	return batchAttemptResult(ricci_xml)

def nodeFence(rc, nodename):
	batch_str = '<module name="cluster"><request API_version="1.0"><function_call name="fence_node"><var mutable="false" name="nodename" type="string" value="%s"/></function_call></request></module>' % nodename

	ricci_xml = rc.batch_run(batch_str)
	return batchAttemptResult(ricci_xml)

def nodeJoinCluster(rc, cluster_startup=False, enable_services=True):
	cstartup = 'false'
	if cluster_startup is True:
		cstartup = 'true'

	enable_svc = 'true'
	if enable_services is False:
		enable_svc = 'false'

	batch_str = '<module name="cluster"><request API_version="1.0"><function_call name="start_node"><var mutable="false" name="cluster_startup" type="boolean" value="%s"/><var mutable="false" name="enable_services" type="boolean" value="%s"/></function_call></request></module>' % (cstartup, enable_svc)

	ricci_xml = rc.batch_run(batch_str)
	return batchAttemptResult(ricci_xml)

def startService(rc, servicename, preferrednode=None):
	if preferrednode is not None:
		batch_str = '<module name="cluster"><request API_version="1.0"><function_call name="start_service"><var mutable="false" name="servicename" type="string" value="%s"/><var mutable="false" name="nodename" type="string" value="%s"/></function_call></request></module>' % (servicename, preferrednode)
	else:
		batch_str = '<module name="cluster"><request API_version="1.0"><function_call name="start_service"><var mutable="false" name="servicename" type="string" value="%s"/></function_call></request></module>' % servicename

	ricci_xml = rc.batch_run(batch_str)
	return batchAttemptResult(ricci_xml)

def migrateService(rc, servicename, preferrednode):
	batch_str = '<module name="cluster"><request API_version="1.0"><function_call name="migrate_service"><var mutable="false" name="servicename" type="string" value="%s"/><var mutable="false" name="nodename" type="string" value="%s" /></function_call></request></module>' % (servicename, preferrednode)

	ricci_xml = rc.batch_run(batch_str)
	return batchAttemptResult(ricci_xml)

def updateServices(rc, enable_list, disable_list):
	batch_list = list()

	if enable_list and len(enable_list) > 0:
		batch_list.append('<module name="service"><request API_version="1.0"><function_call name="enable"><var mutable="false" name="services" type="list_xml">')
		for i in enable_list:
			batch_list.append('<service name="%s"/>' % str(i))
		batch_list.append('</var></function_call></request></module>')

	if disable_list and len(disable_list) > 0:
		batch_list.append('<module name="service"><request API_version="1.0"><function_call name="disable"><var mutable="false" name="services" type="list_xml">')
		for i in disable_list:
			batch_list.append('<service name="%s"/>' % str(i))
		batch_list.append('</var></function_call></request></module>')

	if len(batch_list) < 1:
		return None, None
	ricci_xml = rc.batch_run(''.join(batch_list))
	return batchAttemptResult(ricci_xml)

def restartService(rc, servicename):
	batch_str = '<module name="cluster"><request API_version="1.0"><function_call name="restart_service"><var mutable="false" name="servicename" type="string" value=\"%s\"/></function_call></request></module>' % servicename

	ricci_xml = rc.batch_run(batch_str)
	return batchAttemptResult(ricci_xml)

def stopService(rc, servicename):
	batch_str = '<module name="cluster"><request API_version="1.0"><function_call name="stop_service"><var mutable="false" name="servicename" type="string" value=\"%s\"/></function_call></request></module>' % servicename

	ricci_xml = rc.batch_run(batch_str)
	return batchAttemptResult(ricci_xml)

def svc_manage(rc, hostname, servicename, op):
	svc_func = None

	doc = minidom.Document()
	elem = doc.createElement('result')
	elem.setAttribute('success', '0')

	if not servicename:
		elem.setAttribute('service', 'No service name was specified.')
		elem.setAttribute('message', 'No service name was specified.')

	if not op:
		elem.setAttribute('operation', 'No operation was specified.')
		elem.setAttribute('message', 'No operation was specified.')

	if not servicename or not op:
		doc.appendChild(elem)
		return doc

	elem.setAttribute('service', servicename)
	elem.setAttribute('operation', op)
	elem.setAttribute('hostname', hostname)

	try:
		op = op.strip().lower()
		if op == 'restart' or op == 'start' or op == 'stop':
			svc_func = op
		else:
			raise RicciQueriesError, op
	except Exception, e:
		elem.setAttribute('message', 'Unknown operation: %s' % str(e))
		doc.appendChild(elem)
		return doc

	batch_str = '<module name="service"><request API_version="1.0"><function_call name="%s"><var mutable="false" name="services" type="list_xml"><service name="%s"/></var></function_call></request></module>' % (svc_func, servicename)

	ricci_xml = rc.batch_run(batch_str, async=False)
	if not ricci_xml or not ricci_xml.firstChild:
		elem.setAttribute('message', 'operation failed')
		doc.appendChild(elem)
		return doc

	try:
		mod_elem = ricci_xml.getElementsByTagName('module')
		status_code = int(mod_elem[0].getAttribute('status'))
		if status_code == 0:
			var_elem = mod_elem[0].getElementsByTagName('var')
			for i in var_elem:
				name = i.getAttribute('name').lower()
				if name == 'success':
					success = i.getAttribute('value').lower()
					if success == 'true':
						elem.setAttribute('success', '1')
						elem.setAttribute('message', 'success')
					else:
						elem.setAttribute('message', 'operation failed')
					break
		else:
			err_msg = mod_elem[0].childNodes[1].getAttribute('description')
			elem.setAttribute('message', err_msg)
	except Exception, e:
		elem.setAttribute('message', 'operation failed')

	doc.appendChild(elem)
	return doc

def list_services(rc):
	batch_str = '<module name="service"><request API_version="1.0"><function_call name="list"><var mutable="false" name="description" type="boolean" value="true"/></function_call></request></module>'
	ricci_xml = rc.batch_run(batch_str, async=False)
	if not ricci_xml or not ricci_xml.firstChild:
		return None
	try:
		service_tags = ricci_xml.getElementsByTagName('service')
		return service_tags
	except Exception, e:
		pass

	return None

def nodeIsVirtual(rc):
	batch_str = '<module name="cluster"><request API_version="1.0"><function_call name="virt_guest"/></request></module>'

	ricci_xml = rc.batch_run(batch_str, async=False)
	if not ricci_xml or not ricci_xml.firstChild:
		return None

	var_tags = ricci_xml.getElementsByTagName('var')
	if not var_tags or len(var_tags) < 2:
		return None

	success = False
	virtual = False
	for i in var_tags:
		try:
			name = i.getAttribute('name')
			if not name:
				raise RicciQueriesError, 'name is blank'
			if name == 'success':
				result = i.getAttribute('value')
				if result == 'true':
					success = True
			elif name == 'virt_guest':
				result = i.getAttribute('value')
				if result == 'true':
					virtual = True
			else:
				raise RicciQueriesError, 'unexpected attribute name: %s' % name
		except Exception, e:
			pass

	if not success:
		return None
	return virtual

def getDaemonStates(rc, dlist):
	batch_list = list()
	batch_list.append('<module name="service"><request API_version="1.0"><function_call name="query"><var mutable="false" name="search" type="list_xml">')

	for item in dlist:
		batch_list.append('<service name=\"%s\"/>' % item)
	batch_list.append('</var></function_call></request></module>')

	ricci_xml = rc.batch_run(''.join(batch_list), async=False)
	if not ricci_xml or not ricci_xml.firstChild:
		return {'errors': _('No daemon state info present') }
	return extractDaemonInfo(ricci_xml.firstChild)

def extractDaemonInfo(bt_node):
	resultlist = {}

	svc_nodes = bt_node.getElementsByTagName('service')
	for node in svc_nodes:
		svchash = {}
		try:
			name = node.getAttribute('name')
			if not name:
				raise RicciQueriesError, 'No name'
		except Exception, e:
			name = '[unknown]'
		svchash['name'] = name

		try:
			svc_enabled = node.getAttribute('enabled')
		except Exception, e:
			svc_enabled = '[unknown]'
		svchash['enabled'] = svc_enabled

		try:
			running = node.getAttribute('running')
		except Exception, e:
			running = '[unknown]'
		svchash['running'] = running
		resultlist[name] = svchash

	return resultlist

def getClusterConf(rc):
	import xml.dom

	if rc is None:
		return None

	batch_str = '<module name="cluster"><request API_version="1.0"><function_call name="get_cluster.conf"/></request></module>'

	ricci_xml = rc.batch_run(batch_str, async=False)
	try:
		if not ricci_xml:
			raise RicciQueriesError, 'no XML response'
	except Exception, e:
		return None

	ret = ricci_xml
	var_nodes = ret.getElementsByTagName('var')
	for i in var_nodes:
		if i.getAttribute('name') == 'cluster.conf':
			for j in i.childNodes:
				if j.nodeType == xml.dom.Node.ELEMENT_NODE:
					return j

	return None

def set_xvm_key(rc, key_base64):
	batch_str = '<module name="cluster"><request API_version="1.0"><function_call name="set_xvm_key"><var mutable="false" name="key_base64" type="string" value="%s"/></function_call></request></module>' % key_base64
	ricci_xml = rc.batch_run(batch_str)
	return batchAttemptResult(ricci_xml)

def create_cluster(	rc, 
					cluster_name,
					node_names,
					install_shared_storage,
					upgrade_rpms,
					reboot_nodes=False):

	batch_str = createClusterBatch(cluster_name, node_names,
					True, True, install_shared_storage,
					upgrade_rpms, reboot_nodes)
	ricci_xml = rc.batch_run(batch_str)
	return batchAttemptResult(ricci_xml)

def create_cluster_nodes(	rc, 
							model,
							install_shared_storage,
							upgrade_rpms,
							reboot_nodes=False):

	batch_str = addClusterNodeBatch(model, True, True,
					install_shared_storage, upgrade_rpms, reboot_nodes)
	ricci_xml = rc.batch_run(batch_str)
	return batchAttemptResult(ricci_xml)
