# Copyright (C) 2007-2012 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = 'altname'

class Altname(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

  def getName(self):
    return self.getAttribute('name')

  def setName(self, val):
    return self.addAttribute('name', val)

  def delName(self):
    return self.removeAttribute('name')

  def getPort(self):
    return self.getAttribute('port')

  def setPort(self, val):
    return self.addIntegerAttribute('port', val, (1, 0xffff))

  def delPort(self):
    return self.removeAttribute('port')

  def getMcast(self):
    return self.getAttribute('mcast')

  def setMcast(self, val):
    return self.addAttribute('mcast', val)

  def delMcast(self):
    return self.removeAttribute('mcast')

  def getTTL(self):
    return self.getAttribute('ttl')

  def setTTL(self, val):
    return self.addAttribute('ttl', (1, 255))

  def delTTL(self):
    return self.removeAttribute('ttl')
