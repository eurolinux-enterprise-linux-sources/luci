# Copyright (C) 2006-2010 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = "fence_xvmd"

class FenceXVMd(TagObject):
  DEFAULTS = {
    'port':         '1229',
    'auth':         'sha256',
    'hash':         'sha256',
    'uri':          'qemu:///system',
    'keyfile':      '/etc/cluster/fence_xvm.key',
  }

  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME

  def getDebug(self):
    return self.getAttribute('debug')

  def setDebug(self, val):
    if not val:
        self.removeAttribute('debug')
        return None
    return self.addIntegerAttribute('debug', val)

  def delDebug(self):
    return self.removeAttribute('debug')

  def getPort(self):
    return self.getAttribute('port')

  def setPort(self, val):
    return self.addIntegerAttribute('port', val, (1, 0xffff))

  def delPort(self):
    return self.removeAttribute('port')

  def getUseUUID(self):
    return self.getBinaryAttribute('use_uuid')

  def setUseUUID(self, val):
    return self.addBinaryAttribute('use_uuid', val, (None, '1'))

  def delUseUUID(self):
    return self.removeAttribute('use_uuid')

  def getMulticastAddress(self):
    return self.getAttribute('multicast_address')

  def setMulticastAddress(self, val):
    return self.addAttribute('multicast_address', val)

  def delMulticastAddress(self):
    return self.removeAttribute('multicast_address')

  def getMulticastInterface(self):
    return self.getAttribute('multicast_interface')

  def setMulticastInterface(self, val):
    return self.addAttribute('multicast_interface', val)

  def delMulticastInterface(self):
    return self.removeAttribute('multicast_interface')

  def getAuth(self):
    return self.getAttribute('auth')

  def setAuth(self, val):
    val = val.lower()
    if not val in ('none', 'sha1', 'sha256', 'sha512'):
        raise ValueError, val
    return self.addAttribute('auth', val)

  def delAuth(self):
    return self.removeAttribute('auth')

  def getHash(self):
    return self.getAttribute('hash')

  def setHash(self, val):
    val = val.lower()
    if not val in ('none', 'sha1', 'sha256', 'sha512'):
        raise ValueError, val
    return self.addAttribute('hash', val)

  def delHash(self):
    return self.removeAttribute('hash')

  def getURI(self):
    return self.getAttribute('uri')

  def setURI(self, val):
    return self.addAttribute('uri', val)

  def delURI(self):
    return self.removeAttribute('uri')

  def getKeyFile(self):
    return self.getAttribute('key_file')

  def setKeyFile(self, val):
    return self.addAttribute('key_file', val)

  def delKeyFile(self):
    return self.removeAttribute('key_file')
