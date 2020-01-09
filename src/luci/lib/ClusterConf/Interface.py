# Copyright (C) 2010 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = "interface"

class Interface(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

  def getRingNumber(self):
    return self.getAttribute('ringnumber')

  def setRingNumber(self, val):
    return self.addIntegerAttribute('ringnumber', val)

  def delRingNumber(self):
    return self.removeAttribute('ringnumber')

  def getBindNetAddr(self):
    return self.getAttribute('bindnetaddr')

  def setBindNetAddr(self, val):
    return self.addAttribute('bindnetaddr', val)

  def delBindNetAddr(self):
    return self.removeAttribute('bindnetaddr')

  def getMcastAddr(self):
    return self.getAttribute('mcastaddr')

  def setMcastAddr(self, val):
    return self.addAttribute('mcastaddr', val)

  def delMcastAddr(self):
    return self.removeAttribute('mcastaddr')

  def getMcastPort(self):
    return self.getAttribute('mcastport')

  def setMcastPort(self, val):
    return self.addIntegerAttribute('mcastport', val, (0, 0xffff))

  def delMcastPort(self):
    return self.removeAttribute('mcastport')

  def getBroadcast(self):
    return self.getBinaryAttribute('broadcast')

  def setBroadcast(self, val):
    return self.addBinaryAttribute('broadcast', val, (None, 'yes'))

  def delBroadcast(self):
    return self.removeAttribute('broadcast')
