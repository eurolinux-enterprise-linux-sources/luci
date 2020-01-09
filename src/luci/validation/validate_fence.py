# Copyright (C) 2009-2010 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from luci.lib.helpers import ugettext as _
from luci.lib.ClusterConf.Device import Device
from luci.lib.ClusterConf.FenceDevice import FenceDevice

import logging
log = logging.getLogger(__name__)

FD_PROVIDE_NAME = _('No name was given for this fence device')
FD_PROVIDE_AGENT = _('No fence agent type was given for this fence device')
FI_PROVIDE_PARENT = _('No parent fence device name was given for this fence instance')

FD_NEW_FAIL = _('Error creating fence %s device')
FI_NEW_FAIL = _('Error creating fence %s instance')

def makeNCName(name):
	### name must conform to relaxNG ID type ##
	import re
	ILLEGAL_CHARS = re.compile(':| ')
	return ILLEGAL_CHARS.sub('_', name)

def validateNewFenceDevice(model, **kw):
	fencedev = FenceDevice()

	try:
		ret = validate_fencedevice(model, fencedev, **kw)
		if len(ret) < 1:
			model.addFenceDevice(fencedev)
			return (True, fencedev.getAttribute('name'))
	except Exception, e:
		ret = [ FD_PROVIDE_AGENT ]

	return (False, ret)

def validateFenceDevice(model, **kw):
	try:
		old_fence_name = kw.get('orig_name').strip()
		if not old_fence_name:
			raise Exception, 'blank'
	except Exception, e:
		return (False, [ FD_PROVIDE_NAME ])

	fencedev = None
	try:
		fencedev = model.getFenceDeviceByName(old_fence_name)
		if fencedev is None:
			raise Exception, 'fencedev is None'
	except Exception, e:
		return (False, [ FD_PROVIDE_NAME ])

	try:
		kw['fence_edit'] = True
		ret = validate_fencedevice(model, fencedev, **kw)
		if len(ret) < 1:
			return (True, fencedev.getAttribute('name'))
	except Exception, e:
		ret = [ FD_PROVIDE_NAME ]

	return (False, ret)

def config_fence_attr(params, fence, fname, **kw):
	errors = list()

	for (attr_name, required) in params:
		val = kw.get(attr_name)

		try:
			# passwords may begin and/or end with blank characters
			if not attr_name in ['passwd', 'vmpasswd', 'snmp_priv_passwd']:
				val = val.strip()
			if not val:
				val = None
		except:
			val = None

		if not val:
			if required is True:
				errors.append(_('No value for required attribute "%s" was given for fence "%s"') % (attr_name, fname))
			else:
				try:
					fence.removeAttribute(attr_name)
				except:
					pass
		else:
			fence.addAttribute(attr_name, val)
	return errors

def val_apc_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
 		('ipport', False),
		('login', True),
		('passwd', False),
		('passwd_script', False),
		('power_wait', False),
	)
	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_wti_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
 		('ipport', False),
		('login', True),
		('cmd_prompt', False),
		('passwd', False),
		('passwd_script', False),
		('power_wait', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_virsh_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
 		('ipport', False),
		('login', True),
		('passwd', False),
		('passwd_script', False),
		('power_wait', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_brocade_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
		('login', True),
		('passwd', False),
		('passwd_script', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_vixel_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
		('login', True),
		('cmd_prompt', False),
		('passwd', False),
		('passwd_script', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_mcdata_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
		('login', True),
		('passwd', False),
		('passwd_script', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_gnbd_fd(fencedev, fence_name, **kw):
	params = (
		('servers', True),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_egenera_fd(fencedev, fence_name, **kw):
	params = (
		('cserver', True),
		('esh', False),
		('user', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_sanbox2_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
 		('ipport', False),
		('login', True),
		('cmd_prompt', False),
		('passwd', False),
		('passwd_script', False),
		('power_wait', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_bladecenter_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
 		('ipport', False),
		('login', True),
		('passwd', False),
		('passwd_script', False),
		('power_wait', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_virt_fd(fencedev, fence_name, **kw):
	params = (
		('serial_device', True),
		('serial_params', False),
		('channel_address', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_vmware_soap_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
 		('ipport', False),
		('login', True),
		('passwd', False),
		('passwd_script', False),
		('separator', False),
		('power_wait', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_vmware_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
		('login', True),
		('passwd', False),
		('passwd_script', False),
		('vmlogin', True),
		('vmpasswd', False),
		('vmpasswd_script', False),
		('power_wait', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_scsi_fd(fencedev, fence_name, **kw):
	params = (
		('devices', False),
		('key', False),
		('aptpl', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_lpar_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
		('login', True),
		('cmd_prompt', False),
		('passwd', False),
		('passwd_script', False),
		('hmc_version', False),
		('power_wait', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_bullpap_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
		('login', True),
		('passwd', False),
		('passwd_script', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_noop_fd(fencedev, fence_name, **kw):
	return []

# non-shared devices

def val_rsa_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
 		('ipport', False),
		('login', True),
		('secure', False),
		('identity_file', False),
		('passwd', False),
		('passwd_script', False),
		('cmd_prompt', False),
		('power_wait', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_rsb_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
		('login', True),
		('telnet_port', False),
		('passwd', False),
		('passwd_script', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_eps_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
		('login', True),
		('passwd', False),
		('passwd_script', False),
		('hidden_page', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_drac5_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
 		('ipport', False),
		('login', True),
		('module_name', True),
		('cmd_prompt', False),
		('secure', False),
		('identity_file', False),
		('passwd', False),
		('passwd_script', False),
		('power_wait', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_drac_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
		('login', True),
		('modulename', True),
		('cmd_prompt', False),
		('passwd', False),
		('passwd_script', False),
		('drac_version', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_rps10_fd(fencedev, fence_name, **kw):
	params = (
		('device', True),
		('port', True),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_ipmilan_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
		('login', True),
		('passwd', False),
		('passwd_script', False),
		('auth', False),
		('lanplus', False),
		('cipher', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_alom_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
		('login', True),
		('identity_file', False),
		('passwd', False),
		('passwd_script', False),
		('power_wait', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_ldom_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
		('login', True),
		('identity_file', False),
		('passwd', False),
		('passwd_script', False),
		('cmd_prompt', False),
		('power_wait', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_rackswitch_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
		('identity_file', False),
		('passwd', False),
		('passwd_script', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_xcat_fd(fencedev, fence_name, **kw):
	params = (
		('nodename', True),
		('rpower', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_zvm_fd(fencedev, fence_name, **kw):
	params = (
		('ipl', True),
		('userid', True),
		('ipaddr', True),
		('passwd', False),
		('passwd_script', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_ibmblade_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
 		('udpport', False),
		('login', True),
		('passwd', False),
		('passwd_script', False),
		('community', False),
		('snmp_version', False),
		('snmp_sec_level', False),
		('snmp_auth_prot', False),
		('snmp_priv_prot', False),
		('snmp_priv_passwd', False),
		('snmp_priv_passwd_script', False),
		('power_wait', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_ifmib_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
 		('udpport', False),
		('login', True),
		('passwd', False),
		('passwd_script', False),
		('community', False),
		('snmp_version', False),
		('snmp_sec_level', False),
		('snmp_auth_prot', False),
		('snmp_priv_prot', False),
		('snmp_priv_passwd', False),
		('snmp_priv_passwd_script', False),
		('power_wait', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_cisco_mds_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
 		('udpport', False),
		('login', True),
		('passwd', False),
		('passwd_script', False),
		('community', False),
		('snmp_version', False),
		('snmp_sec_level', False),
		('snmp_auth_prot', False),
		('snmp_priv_prot', False),
		('snmp_priv_passwd', False),
		('snmp_priv_passwd_script', False),
		('power_wait', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_cisco_ucs_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
 		('ipport', False),
		('login', True),
		('passwd', False),
		('passwd_script', False),
		('ssl', False),
		('suborg', False),
		('power_wait', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_cpint_fd(fencedev, fence_name, **kw):
	params = (
		('userid', True),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_apc_snmp_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
 		('udpport', False),
		('login', True),
		('passwd', False),
		('passwd_script', False),
		('community', False),
		('snmp_version', False),
		('snmp_sec_level', False),
		('snmp_auth_prot', False),
		('snmp_priv_prot', False),
		('snmp_priv_passwd', False),
		('snmp_priv_passwd_script', False),
		('power_wait', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_intelmodular_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
 		('udpport', False),
		('login', True),
		('passwd', False),
		('passwd_script', False),
		('community', False),
		('snmp_version', False),
		('snmp_sec_level', False),
		('snmp_auth_prot', False),
		('snmp_priv_prot', False),
		('snmp_priv_passwd', False),
		('snmp_priv_passwd_script', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_ilo_mp_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
 		('ipport', False),
		('login', True),
		('passwd', False),
		('passwd_script', False),
		('secure', False),
		('identity_file', False),
		('cmd_prompt', False),
		('power_wait', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_ilo_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
 		('ipport', False),
		('login', True),
		('passwd', False),
		('passwd_script', False),
		('power_wait', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

def val_rhevm_fd(fencedev, fence_name, **kw):
	params = (
		('ipaddr', True),
 		('ipport', False),
		('login', True),
		('passwd', False),
		('passwd_script', False),
		('ssl', False),
		('power_wait', False),
	)

	errors = config_fence_attr(params, fencedev, fence_name, **kw)
	return errors

FD_VALIDATE = {
	'fence_alom':			val_alom_fd,
	'fence_apc_snmp':		val_apc_snmp_fd,
	'fence_apc':			val_apc_fd,
	'fence_bladecenter':	val_bladecenter_fd,
	'fence_brocade':		val_brocade_fd,
	'fence_bullpap':		val_bullpap_fd,
	'fence_cisco_mds':		val_cisco_mds_fd,
	'fence_cisco_ucs':		val_cisco_ucs_fd,
	'fence_cpint':			val_cpint_fd,
	'fence_drac5':			val_drac5_fd,
	'fence_drac':			val_drac_fd,
	'fence_egenera':		val_egenera_fd,
	'fence_eps':			val_eps_fd,
	'fence_gnbd':			val_gnbd_fd,
	'fence_ibmblade':		val_ibmblade_fd,
	'fence_ifmib':			val_ifmib_fd,
	'fence_ilo_mp':			val_ilo_mp_fd,
	'fence_ilo':			val_ilo_fd,
	'fence_intelmodular':	val_intelmodular_fd,
	'fence_ipmilan':		val_ipmilan_fd,
	'fence_ldom':			val_ldom_fd,
	'fence_lpar':			val_lpar_fd,
	'fence_manual':			val_noop_fd,
	'fence_mcdata':			val_mcdata_fd,
	'fence_rackswitch':		val_rackswitch_fd,
	'fence_rhevm':			val_rhevm_fd,
	'fence_rps10':			val_rps10_fd,
	'fence_rsa':			val_rsa_fd,
	'fence_rsb':			val_rsb_fd,
	'fence_sanbox2':		val_sanbox2_fd,
	'fence_scsi':			val_scsi_fd,
	'fence_virsh':			val_virsh_fd,
	'fence_virt':			val_virt_fd,
	'fence_vixel':			val_vixel_fd,
	'fence_vmware':			val_vmware_fd,
	'fence_vmware_soap':	val_vmware_soap_fd,
	'fence_wti':			val_wti_fd,
	'fence_xcat':			val_xcat_fd,
	'fence_xvm':			val_noop_fd,
	'fence_zvm':			val_zvm_fd,
}

def validate_fencedevice(model, fencedev, **kw):
	try:
		fence_name = kw.get('name').strip()
		if not fence_name:
			raise Exception, 'blank'
		fence_name = makeNCName(fence_name)
	except Exception, e:
		return [ FD_PROVIDE_NAME ]

	name_change = False
	fence_edit = kw.get('fence_edit') is not None

	if fence_edit is True:
		try:
			old_fence_name = kw.get('orig_name').strip()
			if not old_fence_name:
				raise Exception, 'blank'
		except Exception, e:
			return [ FD_PROVIDE_NAME ]

		if old_fence_name != fence_name:
			if model.getFenceDeviceByName(fence_name) is not None:
				return [ FD_PROVIDE_NAME ]
			name_change = True
	else:
		if model.getFenceDeviceByName(fence_name) is not None:
			return [ FD_PROVIDE_NAME ]

	try:
		fence_agent = kw.get('fence_type').strip()
		if not fence_agent:
			raise Exception, 'blank agent'
	except Exception, e:
		return [ FD_PROVIDE_AGENT ]

	fencedev.addAttribute('name', fence_name)
	fencedev.addAttribute('agent', fence_agent)

	try:
		ret = FD_VALIDATE[fence_agent](fencedev, fence_name, **kw)
		if len(ret) < 1 and name_change is True:
			try:
				model.rectifyNewFencedevicenameWithFences(old_fence_name, fence_name)
			except Exception, e:
				log.exception('Error validating %s device %s' % (fence_name, fence_agent))
				return [ FD_NEW_FAIL % fence_agent ]
		return ret
	except Exception, e:
		log.exception('Error validating %s device %s' % (fence_name, fence_agent))
		return [ FD_NEW_FAIL % fence_agent ]

# Validation Methods for Fence Instances

def val_apc_fi(fenceinst, parent_name, **kw):
	params = (
		('port', True),
		('switch', False),
		('secure', False),
		('identity_file', False),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_wti_fi(fenceinst, parent_name, **kw):
	params = (
		('port', True),
		('secure', False),
		('identity_file', False),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_virsh_fi(fenceinst, parent_name, **kw):
	params = (
		('port', True),
		('secure', False),
		('identity_file', False),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_brocade_fi(fenceinst, parent_name, **kw):
	params = (
		('port', True),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_vixel_fi(fenceinst, parent_name, **kw):
	params = (
		('port', True),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_gnbd_fi(fenceinst, parent_name, **kw):
	params = (
		('ipaddress', True),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_sanbox2_fi(fenceinst, parent_name, **kw):
	params = (
		('port', True),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_bladecenter_fi(fenceinst, parent_name, **kw):
	params = (
		('port', True),
		('switch', False),
		('secure', False),
		('identity_file', False),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_mcdata_fi(fenceinst, parent_name, **kw):
	params = (
		('port', True),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_egenera_fi(fenceinst, parent_name, **kw):
	params = (
		('lpan', True),
		('pserver', True),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_lpar_fi(fenceinst, parent_name, **kw):
	params = (
		('partition', True),
		('managed', True),
		('secure', True),
		('identity_file', False),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_bullpap_fi(fenceinst, parent_name, **kw):
	params = (
		('domain', True),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_xvm_fi(fenceinst, parent_name, **kw):
	params = (
		('domain', True),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_virt_fi(fenceinst, parent_name, **kw):
	params = (
		('domain', True),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_vmware_soap_fi(fenceinst, parent_name, **kw):
	params = (
		('ssl', False),
		('port', False),
		('uuid', False),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	if not fenceinst.getAttribute('port') and not fenceinst.getAttribute('uuid'):
		errors.append(_('Either a virtual machine name or UUID must be given'))
	return errors

def val_vmware_fi(fenceinst, parent_name, **kw):
	params = (
		('port', True),
		('secure', False),
		('identity_file', False),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_rackswitch_fi(fenceinst, parent_name, **kw):
	params = (
		('port', True),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_ldom_fi(fenceinst, parent_name, **kw):
	params = (
		('port', True),
		('secure', False),
		('identity_file', False),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_cisco_mds_fi(fenceinst, parent_name, **kw):
	params = (
		('port', True),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_cisco_ucs_fi(fenceinst, parent_name, **kw):
	params = (
		('port', True),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_eps_fi(fenceinst, parent_name, **kw):
	params = (
		('port', True),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_ibmblade_fi(fenceinst, parent_name, **kw):
	params = (
		('port', True),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_ifmib_fi(fenceinst, parent_name, **kw):
	params = (
		('port', True),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_apc_snmp_fi(fenceinst, parent_name, **kw):
	params = (
		('port', True),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_intelmodular_fi(fenceinst, parent_name, **kw):
	params = (
		('port', True),
		('power_wait', False),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_scsi_fi(fenceinst, parent_name, **kw):
	params = (
		('nodename', False),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_rhevm_fi(fenceinst, parent_name, **kw):
	params = (
		('port', True),
	)

	errors = config_fence_attr(params, fenceinst, parent_name, **kw)
	return errors

def val_noop_fi(fenceinst, parent_name, **kw):
	return []

FI_VALIDATE = {
	'fence_alom':			val_noop_fi,
	'fence_apc_snmp':		val_apc_snmp_fi,
	'fence_apc':			val_apc_fi,
	'fence_bladecenter':	val_bladecenter_fi,
	'fence_brocade':		val_brocade_fi,
	'fence_bullpap':		val_bullpap_fi,
	'fence_cisco_mds':		val_cisco_mds_fi,
	'fence_cisco_ucs':		val_cisco_ucs_fi,
	'fence_cpint':			val_noop_fi,
	'fence_drac5':			val_noop_fi,
	'fence_drac':			val_noop_fi,
	'fence_egenera':		val_egenera_fi,
	'fence_eps':			val_eps_fi,
	'fence_gnbd':			val_gnbd_fi,
	'fence_ibmblade':		val_ibmblade_fi,
	'fence_ifmib':			val_ifmib_fi,
	'fence_ilo_mp':			val_noop_fi,
	'fence_ilo':			val_noop_fi,
	'fence_intelmodular':	val_intelmodular_fi,
	'fence_ipmilan':		val_noop_fi,
	'fence_ldom':			val_ldom_fi,
	'fence_lpar':			val_lpar_fi,
	'fence_manual':			val_noop_fi,
	'fence_mcdata':			val_mcdata_fi,
	'fence_rackswitch':		val_rackswitch_fi,
	'fence_rhevm':			val_rhevm_fi,
	'fence_rps10':			val_noop_fi,
	'fence_rsa':			val_noop_fi,
	'fence_rsb':			val_noop_fi,
	'fence_sanbox2':		val_sanbox2_fi,
	'fence_scsi':			val_scsi_fi,
	'fence_virsh':			val_virsh_fi,
	'fence_virt':			val_virt_fi,
	'fence_vixel':			val_vixel_fi,
	'fence_vmware':			val_vmware_fi,
	'fence_vmware_soap':	val_vmware_soap_fi,
	'fence_wti':			val_wti_fi,
	'fence_xcat':			val_noop_fi,
	'fence_xvm':			val_xvm_fi,
	'fence_zvm':			val_noop_fi,
}

def validate_fenceinstance(parent_name, fence_agent, **kw):
	try:
		if not parent_name.strip():
			return (False, [ FI_PROVIDE_PARENT ])
	except:
		return (False, [ FI_PROVIDE_PARENT ])

	fenceinst = Device()
	fenceinst.addAttribute('name', parent_name)
	fenceinst.setAgentType(fence_agent)

	unfence = None

	# XXX: Remove following 4 lines?
	if kw.has_key('option'):
		option = kw.get('option').strip()
		if option:
			fenceinst.addAttribute('option', option)

	try:
		ret = FI_VALIDATE[fence_agent](fenceinst, parent_name, **kw)
		if len(ret) > 0:
			return (False, ret, None)
	except Exception, e:
		log.exception('Error validating fence %s instance of %s' % (fence_agent, parent_name))
		return (False, [ FI_NEW_FAIL % fence_agent ], )

	if kw.has_key('unfencing'):
		# If unfencing required, create and return it's object.
		unfence = fenceinst.clone()
		unfence.addAttribute('action', kw['unfence_action'])
	return (True, fenceinst, unfence)

def getDeviceForInstance(fds, name):
	for fd in fds:
		if fd.getName().strip() == name:
			return fd
	return None

def get_fence_level_info(fence_level, node, fds, major_num, minor_num):
	cur_level = list()
	cur_shared = list()
	kids = node.getFenceMethods()[fence_level - 1].getChildren()

	# This is a marker for allowing multi instances
	# beneath a fencedev
	last_kid_fd = None

	for kid in kids:
		instance_name = kid.getName().strip()
		fd = getDeviceForInstance(fds, instance_name)
		if fd is None:
			continue

		if fd.isShared() is False:
			fencedev = {}
			try:
				fencedev['prettyname'] = fd.getPrettyName()
			except:
				fencedev['unknown'] = True
				fencedev['prettyname'] = fd.getAgentType()
			fencedev['isShared'] = False
			fencedev['id'] = str(major_num)
			fencedev['obj'] = fd
			major_num += 1
			devattrs = fd.getAttributes()
			for k in devattrs.keys():
				fencedev[k] = devattrs[k]
			kidattrs = kid.getAttributes()
			for k in kidattrs.keys():
				if k == 'name':
					continue
				fencedev[k] = kidattrs[k]
			last_kid_fd = None
			cur_level.append(fencedev)
		else:
			if (last_kid_fd is not None) and (fd.getName().strip() == last_kid_fd['name'].strip()):
				instance_struct = {}
				instance_struct['id'] = str(minor_num)
				instance_struct['obj'] = kid
				minor_num += 1
				kidattrs = kid.getAttributes()
				for k in kidattrs.keys():
					if k != 'name':
						instance_struct[k] = kidattrs[k]
				ilist = last_kid_fd['instance_list']
				ilist.append(instance_struct)
				continue
			else:
				# Shared, but not used above
				fencedev = {}
				try:
					fencedev['prettyname'] = fd.getPrettyName()
				except:
					fencedev['unknown'] = True
					fencedev['prettyname'] = fd.getAgentType()
				fencedev['isShared'] = True
				fencedev['id'] = str(major_num)
				fencedev['obj'] = fd
				major_num = major_num + 1
				inlist = list()
				fencedev['instance_list'] = inlist
				devattrs = fd.getAttributes()
				for k in devattrs.keys():
					fencedev[k] = devattrs[k]
				instance_struct = {}
				instance_struct['obj'] = kid
				kidattrs = kid.getAttributes()
				for k in kidattrs.keys():
					if k != 'name':
						instance_struct[k] = kidattrs[k]

				inlist.append(instance_struct)
				cur_level.append(fencedev)
				last_kid_fd = fencedev
				continue

	cur_shared = list()
	for fd in fds:
		isUnique = True
		if fd.isShared() is False:
			continue
		for fdev in cur_level:
			if fd.getName().strip() == fdev['name']:
				isUnique = False
				break
		if isUnique is True:
			shared_struct = {}
			shared_struct['name'] = fd.getName().strip()
			agentname = fd.getAgentType()
			shared_struct['agent'] = agentname
			try:
				shared_struct['prettyname'] = fd.getPrettyName()
			except:
				shared_struct['unknown'] = True
				shared_struct['prettyname'] = agentname
			cur_shared.append(shared_struct)
	return (cur_level, cur_shared, major_num, minor_num)

def getFenceInfo(model, nodename):
    """Return a list of lists containing the level/method and fence instances for that level.

    """

    fence_map = []

    try:
        node = model.retrieveNodeByName(nodename)
    except Exception, e:
        return fence_map

    fds = model.getFenceDevices()
    levels = node.getFenceMethods()
    len_levels = len(levels)

    if len_levels == 0:
        return fence_map

    for level in levels:
        fence_map_level = [0, 0]
        fence_map_level[0] = level
        fence_map_level[1] = []

        for instance in level.getChildren():
            # Lookup, whether the unfencing was set and add a flag appropriately.
            unfencing_flag = False
            for child in node.getChildren():
                if child.getTagName() == 'unfence':
                    unfence = child
                    for child_device in unfence.getChildren():
                        # Try to find existing unfence device that mirrored fence device instance
                        # to be removed and remove it, too.
                        if len(set(instance.getAttributes().items()).difference(child_device.getAttributes().items())) == 0:
                            unfencing_flag = True
                            break
                    break

            fence_map_level[1].append([instance, getDeviceForInstance(fds, instance.getName().strip()), unfencing_flag])
        fence_map.append(fence_map_level)
    return fence_map
