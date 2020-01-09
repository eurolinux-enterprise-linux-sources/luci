# Copyright (C) 2006-2010 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

import FenceDeviceAttr
from TagObject import TagObject

TAG_NAME = "device"
OPTION = "option"

class Device(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.agent_type = ""
    self.has_native_option_set = False

  def getAgentType(self):
    return self.agent_type

  def setAgentType(self, agent_type):
    self.agent_type = agent_type

  def hasNativeOptionSet(self):
    return self.has_native_option_set

  def isPowerController(self):
    return self.agent_type in FenceDeviceAttr.FENCE_POWER_CONTROLLERS

  def addAttribute(self, name, value):
    if name == OPTION:
      self.has_native_option_set = True
    return super(Device, self).addAttribute(name, value)

  def clone(self):
    """Creates a shallow copy of itself."""
    ret = super(Device, self).clone()
    ret.setAgentType(self.getAgentType())
    ret.has_native_option_set = self.has_native_option_set
    return ret
