# Copyright (C) 2006-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = "base_resource"  #This tag name should never be seen

class BaseResource(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.resource_type = ""
    self.deny_all_children = False
    self.refcount = 1
    self.reflist = []
  
  def ref(self):
    self.refcount += 1
    return self.refcount
  
  def unref(self):
    self.refcount -= 1
    return self.refcount

  def getRefcount(self):
    return self.refcount

  def updateRefName(self, old, new):
    for i in self.reflist:
        if i.getAttribute('ref') == old:
            i.addAttribute('ref', new)

  def getResourceType(self):
    return self.resource_type

  def isDenyAll(self):
    return self.deny_all_children

  def getIndependentSubtree(self):
    try:
        ret = int(self.getAttribute('__independent_subtree'))
        if ret == 1:
            return True
    except:
        pass
    return False

  def setIndependentSubtree(self, val):
    return self.addBinaryAttribute('__independent_subtree', val, (None, '1'))

  def delIndependentSubtree(self):
    return self.removeAttribute('__independent_subtree')

  def getNonCriticalResource(self):
    try:
        ret = int(self.getAttribute('__independent_subtree'))
        if ret == 2:
            return True
    except:
        pass
    return False

  def setNonCriticalResource(self, val):
    return self.addBinaryAttribute('__independent_subtree', val, (None, '2'))

  def delNonCriticalResource(self):
    return self.removeAttribute('__independent_subtree')

  def getEnforceTimeouts(self):
    return self.getBinaryAttribute('__enforce_timeouts')

  def setEnforceTimeouts(self, val):
    return self.addBinaryAttribute('__enforce_timeouts', val, (None, '1'))

  def delEnforceTimeouts(self):
    return self.removeAttribute('__enforce_timeouts')

  def getMaxFailures(self):
    return self.getAttribute('__max_failures')

  def setMaxFailures(self, val):
    return self.addIntegerAttribute('__max_failures', val, (0, None))

  def delMaxFailures(self):
    return self.removeAttribute('__max_failures')

  def getFailureExpireTime(self):
    return self.getAttribute('__failure_expire_time')

  def setFailureExpireTime(self, val):
    return self.addIntegerAttribute('__failure_expire_time', val, (0, None))

  def delFailureExpireTime(self):
    return self.removeAttribute('__failure_expire_time')

  def getResMaxRestarts(self):
    return self.getAttribute('__max_restarts')

  def setResMaxRestarts(self, val):
    return self.addIntegerAttribute('__max_restarts', val, (0, None))

  def delResMaxRestarts(self):
    return self.removeAttribute('__max_restarts')

  def getResRestartExpireTime(self):
    return self.getAttribute('__restart_expire_time')

  def setResRestartExpireTime(self, val):
    return self.addIntegerAttribute('__restart_expire_time', val, (0, None))

  def delResRestartExpireTime(self):
    return self.removeAttribute('__restart_expire_time')

  def delSubtreeProperties(self):
	self.delIndependentSubtree()
	self.delEnforceTimeouts()
	self.delMaxFailures()
	self.delFailureExpireTime()
	self.delResMaxRestarts()
	self.delResRestartExpireTime()
