# Copyright (C) 2006-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = "multicast"

class Multicast(TagObject):
  DEFAULTS = {
    'ttl':      '1',
  }
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.attr_hash.update(self.DEFAULTS)

  def getAddr(self):
    return self.getAttribute('addr')

  def setAddr(self, val):
    return self.addAttribute('addr', val)

  def delAddr(self):
    return self.removeAttribute('addr')

  def getTTL(self):
    return self.getAttribute('ttl')

  def setTTL(self, val):
    return self.addIntegerAttribute('ttl', val, (0, 255))

  def delTTL(self):
    return self.removeAttribute('ttl')

  def removeDefaults(self):
    if self.getTTL() == self.DEFAULTS.get('ttl'):
        self.delTTL()
