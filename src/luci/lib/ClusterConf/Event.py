# Copyright (C) 2010 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = "event"

class Event(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

  def getFile(self):
    return self.getAttribute('file')

  def getPriority(self):
    return self.getAttribute('priority')

  def getClass(self):
    return self.getAttribute('class')

  def getService(self):
    return self.getAttribute('service')

  def getServiceState(self):
    return self.getAttribute('service_state')

  def getServiceOwner(self):
    return self.getAttribute('service_owner')

  def getNode(self):
    return self.getAttribute('node')

  def getNodeID(self):
    return self.getAttribute('node_id')
    
  def getNodeState(self):
    return self.getBinaryAttribute('node_state')
    
  def getNodeClean(self):
    return self.getBinaryAttribute('node_clean')

  def getNodeLocal(self):
    return self.getBinaryAttribute('node_local')

  def getScript(self):
    return self.element_text

  def setScript(self, val):
    self.element_text = val
    return self.element_text
