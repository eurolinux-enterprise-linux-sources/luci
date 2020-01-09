# Copyright (C) 2010-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = 'logging'
    
syslog_priority_dict = {
    0: 'emerg',
    1: 'alert',
    2: 'crit',
    3: 'err',
    4: 'warning',
    5: 'notice',
    6: 'info',
    7: 'debug',
}

class Logging(TagObject):
  DEFAULTS = {
    'to_syslog':        '1',
    'to_logfile':       '1',
    'syslog_facility':  'daemon',
    'syslog_priority':  'info',
    'logfile_priority': 'info',
  }

  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.attr_hash.update(self.DEFAULTS)

  def getSyslog(self):
    return self.getBinaryAttribute('to_syslog')

  def setSyslog(self, val):
    return self.addBinaryAttribute('to_syslog', val, ('no', 'yes'))

  def delSyslog(self):
    return self.removeAttribute('to_syslog')

  def getLogfile(self):
    return self.getBinaryAttribute('to_logfile')

  def setLogfile(self, val):
    return self.addBinaryAttribute('to_logfile', val, ('no', 'yes'))

  def delLogfile(self):
    return self.removeAttribute('to_logfile')

  def getLogfilePath(self):
    return self.getAttribute('logfile')

  def setLogfilePath(self, path):
    return self.addAttribute('logfile', path)
    
  def delLogfilePath(self):
    return self.removeAttribute('logfile')
    
  def getSyslogFacility(self):
    return self.getAttribute('syslog_facility')

  def setSyslogFacility(self, val):
    val = val.lower()
    if not val in ('auth', 'authpriv', 'cron', 'daemon', 'kern',
                   'lpr', 'mail', 'news', 'syslog', 'user', 'uucp',
                   'local0', 'local1', 'local2', 'local3',
                   'local4', 'local5', 'local6', 'local7'):
        raise ValueError, "Invalid syslog facility: %s" % val
    return self.addAttribute('syslog_facility', val)

  def delSyslogFacility(self):
    return self.removeAttribute('syslog_facility')

  def getSyslogPriority(self):
    return self.getAttribute('syslog_priority')

  def setSyslogPriority(self, val):
    return self.addAttribute('syslog_priority', val)

  def delSyslogPriority(self):
    return self.removeAttribute('syslog_priority')

  def getLogfilePriority(self):
    val = self.getAttribute('logfile_priority')
    if val:
        try:
            return syslog_priority_dict[int(val)]
        except:
            pass
    return val

  def setLogfilePriority(self, val):
    val = val.lower()
    if not val in syslog_priority_dict.values():
        try:
            val = syslog_priority_dict[int(val)]
        except:
            raise ValueError, "Invalid syslog priority: %s" % val
    return self.addAttribute('logfile_priority', val)

  def delLogfilePriority(self):
    return self.removeAttribute('logfile_priority')

  def getDebug(self):
    return self.getBinaryAttribute('debug')

  def setDebug(self, val):
    return self.addBinaryAttribute('debug', val, (None, 'on'))

  def delDebug(self):
    return self.removeAttribute('debug')

  def getDaemonConfig(self, name):
    name = name.lower()
    for i in self.children:
        if name == i.getName().lower():
            if name != 'corosync':
                return i
            if not i.getSubsys():
                return i
    return None

  def setDaemonConfig(self, obj):
    stale_obj = []
    daemon = obj.getName().lower()
    for i in self.children:
        if daemon == i.getName().lower():
            # corosync may have multiple entries for different subsystems
            if daemon != 'corosync':
                stale_obj.append(i)
            else:
                if not i.getSubsys():
                    stale_obj.append(i)

    for i in stale_obj:
        self.removeChild(i)
    self.addChild(obj)

  def delDaemonConfig(self, name):
    conf_obj = self.getDaemonConfig(name)
    if conf_obj is not None:
        self.removeChild(conf_obj)

  def getCorosyncSubsysConfig(self, subsys):
    subsys = subsys.upper()
    for i in self.children:
        if i.getName().lower() == 'corosync':
            cur_subsys = i.getSubsys()
            if cur_subsys and subsys == cur_subsys.upper():
                return i
    return None

  def setCorosyncSubsysConfig(self, obj):
    subsys_conf = self.getCorosyncSubsysConfig(obj.getSubsys())
    if subsys_conf:
        self.removeChild(subsys_conf)
    self.addChild(obj)

  def delCorosyncSubsysConfig(self, subsys):
    subsys_conf_obj = self.getCorosyncSubsysConfig(subsys)
    if subsys_conf_obj is not None:
        self.removeChild(subsys_conf_obj)

  def removeDefaults(self):
    if self.getSyslog() == int(self.DEFAULTS.get('to_syslog')):
        self.delSyslog()
    if self.getLogfile() == int(self.DEFAULTS.get('to_logfile')):
        self.delLogfile()
    if self.getSyslogFacility() == self.DEFAULTS.get('syslog_facility'):
        self.delSyslogFacility()
    if self.getSyslogPriority() == self.DEFAULTS.get('syslog_priority'):
        self.delSyslogPriority()
    if self.getLogfilePriority() == self.DEFAULTS.get('logfile_priority'):
        self.delLogfilePriority()
