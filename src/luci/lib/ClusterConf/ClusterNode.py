# Copyright (C) 2006-2012 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject
from Fence import Fence
from Method import Method

import logging
log = logging.getLogger(__name__)

TAG_NAME = "clusternode"

class ClusterNode(TagObject):
  DEFAULTS = {
    'votes':    '1',
  }
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.attr_hash.update(self.DEFAULTS)

  def getFenceNode(self):
    ret = None
    for child in self.children:
        if child.getTagName() == 'fence':
            ret = child
            break
    if ret is None:
        ret = Fence()
        self.addChild(ret)
    return ret

  def getFenceMethods(self):
    # This method returns the set of 'method' objs.
    ret = list()
    for i in self.getFenceNode().getChildren():
      if type(i) is not Method:
        if not i.errors:
          i.errors = True
          log.error('Error parsing cluster XML: expected method element, got %s' % i.getTagName())
      else:
        ret.append(i)
    return ret  

  def getVotes(self):
    votes = self.getAttribute('votes')
    if votes is None:
        return '1'
    return votes

  def setVotes(self, val):
    return self.addIntegerAttribute('votes', val, (1, None))

  def delVotes(self):
    return self.removeAttribute('votes')

  def getWeight(self):
    return self.getAttribute('weight')

  def setWeight(self, val):
    return self.addIntegerAttribute('weight', val, (0, None))

  def delWeight(self):
    return self.removeAttribute('weight')

  def getNodeID(self):
    return self.getAttribute('nodeid')

  def setNodeID(self, val):
    return self.addIntegerAttribute('nodeid', val, (1, None))

  def getAltname(self):
    for i in self.children:
        if i.getTagName() == 'altname':
            return i
    return None

  def delAltname(self):
    cur_altname = self.getAltname()
    if cur_altname is not None:
        self.removeChild(cur_altname)

  def setAltname(self, an_node):
    self.delAltname()
    self.addChild(an_node)

  # Cluster2/RHEL5 only
  def getIfname(self):
    return self.getAttribute('ifname')

  # Cluster2/RHEL5 only
  def setIfname(self, val):
    return self.addAttribute('ifname', val)

  # Cluster2/RHEL5 only
  def delIfname(self):
    return self.removeAttribute('ifname')

  def removeFenceInstance(self, method, instance):
    """Remove fence instance from this node and given fence method."""
    for child in self.children:
      if child.getTagName() == 'unfence':
        unfence = child
        for child_device in unfence.children:
          # Try to find existing unfence device that mirrored fence device instance
          # to be removed and remove it, too.
          if len(set(instance.getAttributes().items()).difference(child_device.getAttributes().items())) == 0:
            unfence.removeChild(child_device)
            if len(unfence.children) == 0:
              # Remove the whole 'unfence' section from within 'node' section
              # if it is empty.
              self.removeChild(unfence)
            break
        break
    method.removeChild(instance)

  def removeDefaults(self):
    if self.getVotes() == self.DEFAULTS.get('votes'):
        self.delVotes()
