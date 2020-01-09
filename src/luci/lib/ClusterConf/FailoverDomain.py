# Copyright (C) 2006-2012 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject
from FailoverDomainNode import FailoverDomainNode

import logging
log = logging.getLogger(__name__)

TAG_NAME = "failoverdomain"

class FailoverDomain(TagObject):
  DEFAULTS = {
    'ordered':      '0',
    'restricted':   '0',
    'nofailback':   '0',
  }
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.attr_hash.update(self.DEFAULTS)

  def getRestricted(self):
    return self.getBinaryAttribute('restricted')

  def setRestricted(self, val):
    return self.addBinaryAttribute('restricted', val, ('0', '1'))

  def delRestricted(self):
    return self.removeAttribute('restricted')

  def getOrdered(self):
    return self.getBinaryAttribute('ordered')

  def setOrdered(self, val):
    return self.addBinaryAttribute('ordered', val, ('0', '1'))

  def delOrdered(self):
    return self.removeAttribute('ordered')

  def getNoFailback(self):
    return self.getBinaryAttribute('nofailback')

  def setNoFailback(self, val):
    return self.addBinaryAttribute('nofailback', val, (None, '1'))

  def delNoFailback(self):
    return self.removeAttribute('nofailback')

  def getFailoverDomainNodes(self):
    ret = list()
    for i in self.getChildren():
      if type(i) is not FailoverDomainNode:
        if not i.errors:
          i.errors = True
          log.error('Error parsing cluster XML: expected failoverdomainnode element, got %s' % i.getTagName())
      else:
        ret.append(i)
    return ret  

  def get_member_node(self, nodename):
    for i in self.getFailoverDomainNodes():
        if i.getName() == nodename:
            return i
    return None

  def has_member_node(self, nodename):
    return self.get_member_node(nodename) != None

  def clear_member_nodes(self):
    self.children = list()

  def removeDefaults(self):
    if self.getRestricted() == self.DEFAULTS.get('restricted'):
        self.delRestricted()
    if self.getOrdered() == self.DEFAULTS.get('ordered'):
        self.delOrdered()
    if self.getNoFailback() == self.DEFAULTS.get('nofailback'):
        self.delNoFailback()
