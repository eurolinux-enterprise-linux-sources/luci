# Copyright (C) 2010-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = 'clvmd'

class Clvmd(TagObject):
  DEFAULTS = {
    'interface':        'cman',
  }
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

  def getInterface(self):
    return self.getAttribute('interface')

  def setInterface(self, val):
    val = val.lower()
    if not val in ('cman', 'corosync', 'openais'):
        raise ValueError, "Invalid clvmd interface value: %s" % val
    return self.addAttribute('interface', val)

  def delInterface(self):
    return self.removeAttribute('interface')

  def removeDefaults(self):
    if self.getInterface() == self.DEFAULTS.get('interface'):
        self.delInterface()
