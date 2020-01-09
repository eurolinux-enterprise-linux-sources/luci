# Copyright (C) 2006-2010 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = "service"

class Service(TagObject):
  DEFAULTS = {
    'autostart':        '1',
    'nfslock':          '0',
    'nfs_client_cache': '0',
    'exclusive':        '0',
    'depend_mode':      'hard',
  }
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.attr_hash.update(self.DEFAULTS)

  def getAutostart(self):
    return self.getBinaryAttribute('autostart')

  def setAutostart(self, val):
    return self.addBinaryAttribute('autostart', val, ('0', '1'))

  def delAutostart(self):
    return self.removeAttribute('autostart')

  def getExclusive(self):
    return self.getAttribute('exclusive')

  def getExclusiveBinary(self):
    return self.getBinaryAttribute('exclusive')

  def setExclusive(self, val):
    return self.addIntegerAttribute('exclusive', val, (0, None))

  def delExclusive(self):
    return self.removeAttribute('exclusive')

  def getFailoverDomain(self):
    return self.getAttribute('domain')

  def setFailoverDomain(self, val):
    return self.addAttribute('domain', val)

  def delFailoverDomain(self):
    return self.removeAttribute('domain')

  def getRecoveryPolicy(self):
    return self.getAttribute('recovery')

  def setRecoveryPolicy(self, val):
    return self.addAttribute('recovery', val)

  def delRecoveryPolicy(self):
    return self.removeAttribute('recovery')

  def getNFSLock(self):
    return self.getBinaryAttribute('nfslock')

  def setNFSLock(self, val):
    return self.addBinaryAttribute('nfslock', val, (None, '1'))

  def delNFSLock(self):
    return self.removeAttribute('nfslock')

  def getNFSClientCache(self):
    return self.getBinaryAttribute('nfs_client_cache')

  def setNFSClientCache(self, val):
    return self.addBinaryAttribute('nfs_client_cache', val, (None, '1'))

  def delNFSClientCache(self):
    return self.removeAttribute('nfs_client_cache')

  def getMaxRestarts(self):
    return self.getAttribute('max_restarts')

  def setMaxRestarts(self, val):
    return self.addIntegerAttribute('max_restarts', val, (0, None))

  def delMaxRestarts(self):
    return self.removeAttribute('max_restarts')

  def getRestartExpireTime(self):
    return self.getAttribute('restart_expire_time')

  def setRestartExpireTime(self, val):
    return self.addIntegerAttribute('restart_expire_time', val, (0, None))

  def delRestartExpireTime(self):
    return self.removeAttribute('restart_expire_time')

  def getPriority(self):
    return self.getAttribute('priority')

  def setPriority(self, val):
    return self.addIntegerAttribute('priority', val)

  def delPriority(self):
    return self.removeAttribute('priority')

  def getDependMode(self):
    return self.getAttribute('depend_mode')

  def setDependMode(self, val):
    val = val.lower()
    if val not in ('hard', 'soft'):
        raise ValueError, val
    return self.addAttribute('depend_mode', val)

  def delDependMode(self):
    return self.removeAttribute('depend_mode')

  def getDepend(self):
    return self.getAttribute('depend')

  def setDepend(self, val):
    return self.addAttribute('depend', val)

  def delDepend(self):
    return self.removeAttribute('depend')

  def removeDefaults(self):
    if self.getAutostart() == int(self.DEFAULTS.get('autostart')):
        self.delAutostart()
    if self.getNFSLock() == int(self.DEFAULTS.get('nfslock')):
        self.delNFSLock()
    if self.getNFSClientCache() == int(self.DEFAULTS.get('nfs_client_cache')):
        self.delNFSClientCache()
    if self.getExclusive() == self.DEFAULTS.get('exclusive'):
        self.delExclusive()
    if not self.getDepend() or self.getDependMode() == self.DEFAULTS.get('depend_mode'):
        self.delDependMode()
