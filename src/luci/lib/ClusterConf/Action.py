# Copyright (C) 2010 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = "action"

class Action(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

  def getDepth(self):
    return self.getAttribute('depth')

  def setDepth(self, val):
    return self.addAttribute('depth', val)

  def delDepth(self):
    return self.removeAttribute('depth')

  def getInterval(self):
    return self.getAttribute('interval')

  def setInterval(self, val):
    return self.addIntegerAttribute('interval', val, (0, None))

  def delInterval(self):
    return self.removeAttribute('interval')

  def getTimeout(self):
    return self.getAttribute('timeout')

  def setTimeout(self, val):
    return self.addIntegerAttribute('timeout', val, (0, None))

  def delTimeout(self):
    return self.removeAttribute('timeout')
