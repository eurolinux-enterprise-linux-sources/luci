# Copyright (C) 2010-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = 'dlm'

class DLM(TagObject):
  DEFAULTS = {
    'protocol':             'detect',
    'timewarn':             '500',
    'log_debug':            '0',
    'enable_fencing':       '1',
    'enable_deadlk':        '0',
    'enable_quorum':        '0',
    'enable_plock':         '1',
    'plock_debug':   '0',
    'plock_ownership':      '1',
    'plock_rate_limit':     '0',
    'drop_resources_time':  '10000',
    'drop_resources_count': '10',
    'drop_resources_age':   '10000',
  }

  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.attr_hash.update(self.DEFAULTS)

  def getLogDebug(self):
    return self.getBinaryAttribute('log_debug')

  def setLogDebug(self, val):
    return self.addBinaryAttribute('log_debug', val, ('0', '1'))

  def delLogDebug(self):
    return self.removeAttribute('log_debug')

  def getEnableFencing(self):
    return self.getBinaryAttribute('enable_fencing')

  def setEnableFencing(self, val):
    return self.addBinaryAttribute('enable_fencing', val, ('0', '1'))

  def delEnableFencing(self):
    return self.removeAttribute('enable_fencing')

  def getEnableQuorum(self):
    return self.getBinaryAttribute('enable_quorum')

  def setEnableQuorum(self, val):
    return self.addBinaryAttribute('enable_quorum', val, ('0', '1'))

  def delEnableQuorum(self):
    return self.removeAttribute('enable_quorum')

  def getEnableDeadlk(self):
    return self.getBinaryAttribute('enable_deadlk')

  def delEnableDeadlk(self):
    return self.removeAttribute('enable_deadlk')

  def setEnableDeadlk(self, val):
    return self.addBinaryAttribute('enable_deadlk', val, ('0', '1'))

  def getEnablePlock(self):
    return self.getBinaryAttribute('enable_plock')

  def setEnablePlock(self, val):
    return self.addBinaryAttribute('enable_plock', val, ('0', '1'))

  def delEnablePlock(self):
    return self.removeAttribute('enable_plock')

  def getPlockDebug(self):
    return self.getBinaryAttribute('plock_debug')

  def setPlockDebug(self, val):
    return self.addBinaryAttribute('plock_debug', val, ('0', '1'))

  def delPlockDebug(self):
    return self.removeAttribute('plock_debug')

  def getPlockRateLimit(self):
    return self.getBinaryAttribute('plock_rate_limit')

  def setPlockRateLimit(self, val):
    return self.addBinaryAttribute('plock_rate_limit', val, ('0', '1'))

  def delPlockRateLimit(self):
    return self.removeAttribute('plock_rate_limit')

  def getPlockOwnership(self):
    return self.getBinaryAttribute('plock_ownership')

  def setPlockOwnership(self, val):
    return self.addBinaryAttribute('plock_ownership', val, ('0', '1'))

  def delPlockOwnership(self):
    return self.removeAttribute('plock_ownership')

  def getTimeWarn(self):
    return self.getAttribute('timewarn')

  def setTimeWarn(self, val):
    return self.addIntegerAttribute('timewarn', val, (0, None))

  def delTimeWarn(self):
    return self.removeAttribute('timewarn')

  def getProtocol(self):
    proto = self.getAttribute('protocol')
    if proto:
        return proto.lower()
    return proto

  def setProtocol(self, val):
    proto = val.lower()
    if not proto in ('detect', 'tcp', 'sctp'):
        raise ValueError, val
    return self.addAttribute('protocol', proto)

  def delProtocol(self):
    return self.removeAttribute('protocol')

  def getDropResourcesTime(self):
    return self.getAttribute('drop_resources_time')

  def setDropResourcesTime(self, val):
    return self.addIntegerAttribute('drop_resources_time', val, (0, None))

  def delDropResourcesTime(self):
    return self.removeAttribute('drop_resources_time')

  def getDropResourcesCount(self):
    return self.getAttribute('drop_resources_count')

  def setDropResourcesCount(self, val):
    return self.addIntegerAttribute('drop_resources_count', val, (0, None))

  def delDropResourcesCount(self):
    return self.removeAttribute('drop_resources_count')

  def getDropResourcesAge(self):
    return self.getAttribute('drop_resources_age')

  def setDropResourcesAge(self, val):
    return self.addIntegerAttribute('drop_resources_age', val, (0, None))

  def delDropResourcesAge(self):
    return self.removeAttribute('drop_resources_age')

  def getLockspace(self, lkspace_name):
    for i in self.children:
        if i.getName() == lkspace_name:
            return i
    return None

  def delLockspace(self, lkspace_name):
    del_node = None
    for i in self.children:
        if i.getName() == lkspace_name:
            del_node = i
            break
    if del_node is not None:
        self.removeChild(del_node)
        return True
    return False

  def addLockspace(self, lkspace_node):
    self.addChild(lkspace_node)

  def removeDefaults(self):
    if self.getProtocol() == self.DEFAULTS.get('protocol'):
        self.delProtocol()
    if self.getTimeWarn() == self.DEFAULTS.get('timewarn'):
        self.delTimeWarn()
    if self.getLogDebug() == int(self.DEFAULTS.get('log_debug')):
        self.delLogDebug()
    if self.getEnableFencing() == int(self.DEFAULTS.get('enable_fencing')):
        self.delEnableFencing()
    if self.getEnableDeadlk() == int(self.DEFAULTS.get('enable_deadlk')):
        self.delEnableDeadlk()
    if self.getEnableQuorum() == int(self.DEFAULTS.get('enable_quorum')):
        self.delEnableQuorum()
    if self.getEnablePlock() == int(self.DEFAULTS.get('enable_plock')):
        self.delEnablePlock()
    if self.getPlockOwnership() == int(self.DEFAULTS.get('plock_ownership')):
        self.delPlockOwnership()
    if self.getPlockDebug() == int(self.DEFAULTS.get('plock_debug')):
        self.delPlockDebug()
    if self.getPlockRateLimit() == int(self.DEFAULTS.get('plock_rate_limit')):
        self.delPlockRateLimit()
    if self.getDropResourcesTime() == self.DEFAULTS.get('drop_resources_time'):
        self.delDropResourcesTime()
    if self.getDropResourcesCount() == self.DEFAULTS.get('drop_resources_count'):
        self.delDropResourcesCount()
    if self.getDropResourcesAge() == self.DEFAULTS.get('drop_resources_age'):
        self.delDropResourcesAge()
