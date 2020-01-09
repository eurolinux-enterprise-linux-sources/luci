# Copyright (C) 2010-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = 'group'

class Group(TagObject):
  DEFAULTS = {
    'groupd_compat':        '0',
  }
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.attr_hash.update(self.DEFAULTS)

  def getCompat(self):
    return self.getBinaryAttribute('groupd_compat')

  def setCompat(self, val):
    return self.addBinaryAttribute('groupd_compat', val, (None, '1'))

  def delCompat(self):
    return self.removeAttribute('groupd_compat')

  def removeDefaults(self):
    if self.getCompat() == int(self.DEFAULTS.get('groupd_compat')):
        self.delCompat()
