# Copyright (C) 2006-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = "rm"

class Rm(TagObject):
  DEFAULTS = {
    'central_processing':       '0',
    'transition_throttling':    '5',
    'status_child_max':         '5',
    'status_poll_interval':     '10',
  }
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.attr_hash.update(self.DEFAULTS)

  def getStatusChildMax(self):
    return self.getAttribute('status_child_max')

  def setStatusChildMax(self, val):
    return self.addIntegerAttribute('status_child_max', val, (0, None))

  def delStatusChildMax(self):
    return self.removeAttribute('status_child_max')

  def getStatusPollInterval(self):
    return self.getAttribute('status_poll_interval')

  def setStatusPollInterval(self, val):
    return self.addIntegerAttribute('status_poll_interval', val, (0, None))

  def delStatusPollInterval(self):
    return self.removeAttribute('status_poll_interval')

  def getCentralProcessing(self):
    return self.getBinaryAttribute('central_processing')

  def setCentralProcessing(self, val):
    return self.addBinaryAttribute('central_processing', val, (None, '1'))

  def delCentralProcessing(self):
    return self.removeAttribute('central_processing')

  def getTransitionThrottling(self):
    return self.getAttribute('transition_throttling')

  def setTransitionThrottling(self, val):
    return self.addIntegerAttribute('transition_throttling', val, (0, None))

  def delTransitionThrottling(self):
    return self.removeAttribute('transition_throttling')

  def removeDefaults(self):
    if self.getCentralProcessing() == int(self.DEFAULTS.get('central_processing')):
        self.delCentralProcessing()
    if self.getStatusChildMax() == self.DEFAULTS.get('status_child_max'):
        self.delStatusChildMax()
    if self.getStatusPollInterval() == self.DEFAULTS.get('status_poll_interval'):
        self.delStatusPollInterval()
    if self.getTransitionThrottling() == self.DEFAULTS.get('transition_throttling'):
        self.delTransitionThrottling()
