# Copyright (C) 2010 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from Logging import Logging

TAG_NAME = "logging_daemon"

class LoggingDaemon(Logging):
  def __init__(self):
    Logging.__init__(self)
    self.TAG_NAME = TAG_NAME

  def emptyTag(self):
    if len(self.comments) != 0 or len(self.trailing_comments) != 0 or self.element_text:
       return False

    attr_len = len(self.attr_hash)
    if attr_len == 1 and self.getName():
        return True
    if attr_len == 2 and self.getName() == 'corosync' and self.getSubsys():
        return True
    return False

  def getSubsys(self):
    return self.getAttribute('subsys')

  def setSubsys(self, val):
    return self.addAttribute('subsys', val)

  def delSubsys(self):
    return self.removeAttribute('subsys')
