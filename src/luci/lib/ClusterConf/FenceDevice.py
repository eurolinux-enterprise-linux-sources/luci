# Copyright (C) 2006-2010 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

import FenceDeviceAttr
from TagObject import TagObject

TAG_NAME = "fencedevice"

class FenceDevice(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

  def getAgentType(self):
    agent = self.attr_hash.get('agent')
    try:
      return agent[agent.rfind('/') + 1:]
    except:
      pass
    return agent

  def getPrettyName(self):
    agent_type = self.getAgentType()
    pname = FenceDeviceAttr.FENCE_OPTS.get(agent_type)
    if pname is None:
        return agent_type
    return pname

  def isShared(self):
    agent = self.getAgentType()
    if agent == "fence_drac": #2 variants of drac...
      mname = self.getAttribute("modulename")
      if not mname:
        return False
      else:
        return True
    return FenceDeviceAttr.FENCE_SHARED.has_key(agent)
