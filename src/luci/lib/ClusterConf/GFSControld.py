# Copyright (C) 2010-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = 'gfs_controld'

class GFSControld(TagObject):
  DEFAULTS = {
    'enable_withdraw':          '1',
    'enable_plock':             '1',
    'plock_debug':              '0',
    'plock_rate_limit':         '0',
    'plock_ownership':          '1',
    'drop_resources_time':      '10000',
    'drop_resources_count':     '10',
    'drop_resources_age':       '10000',
  }

  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.attr_hash.update(self.DEFAULTS)

  def getEnableWithdraw(self):
    return self.getBinaryAttribute('enable_withdraw')

  def setEnableWithdraw(self, val):
    return self.addBinaryAttribute('enable_withdraw', val, ('0', '1'))

  def delEnableWithdraw(self):
    return self.removeAttribute('enable_withdraw')

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

  def removeDefaults(self):
    if self.getEnableWithdraw() == int(self.DEFAULTS.get('enable_withdraw')):
        self.delEnableWithdraw()
    if self.getEnablePlock() == int(self.DEFAULTS.get('enable_plock')):
        self.delEnablePlock()
    if self.getPlockDebug() == int(self.DEFAULTS.get('plock_debug')):
        self.delPlockDebug()
    if self.getPlockRateLimit() == int(self.DEFAULTS.get('plock_rate_limit')):
        self.delPlockRateLimit()
    if self.getPlockOwnership() == int(self.DEFAULTS.get('plock_ownership')):
        self.delPlockOwnership()
    if self.getDropResourcesTime() == self.DEFAULTS.get('drop_resources_time'):
        self.delDropResourcesTime()
    if self.getDropResourcesCount() == self.DEFAULTS.get('drop_resources_count'):
        self.delDropResourcesCount()
    if self.getDropResourcesAge() == self.DEFAULTS.get('drop_resources_age'):
        self.delDropResourcesAge()
