# Copyright (C) 2006-2010 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = "failoverdomainnode"

class FailoverDomainNode(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

  def getPriority(self):
    return self.getAttribute('priority')

  def setPriority(self, val):
    self.addIntegerAttribute('priority', val, (1, 100))

  def delPriority(self):
    return self.removeAttribute('priority')
