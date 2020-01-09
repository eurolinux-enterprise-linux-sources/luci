# Copyright (C) 2012 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = 'altmulticast'

class Altmulticast(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

  def getAddr(self):
    return self.attr_hash.get('addr')

  def setAddr(self, val):
    return self.addAttribute('addr', val)

  def delAddr(self):
    return self.attr_hash.get('addr')

  def getPort(self):
    return self.getAttribute('port')

  def setPort(self, val):
    return self.addIntegerAttribute('port', val, (1, 0xffff))

  def delPort(self):
    return self.removeAttribute('port')

  def getTTL(self):
    return self.getAttribute('ttl')

  def setTTL(self, val):
    return self.addIntegerAttribute('ttl', val, (1, 255))

  def delTTL(self):
    return self.removeAttribute('ttl')
