# Copyright (C) 2006-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = 'totem'

class Totem(TagObject):
  DEFAULTS = {
    'join':                                 '60',
    'token':                                '10000',
    'fail_recv_const':                      '2500',
    'token_retransmits_before_loss_const':  '20',
    'consensus':                            '4800',
    'secauth':                              '1',
  }

  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.attr_hash.update(self.DEFAULTS)

  def getJoinTimeout(self):
    return self.getAttribute('join')

  def setJoinTimeout(self, val):
    return self.addIntegerAttribute('join', val, (0, None))

  def delJoinTimeout(self):
    return self.removeAttribute('join')

  def getTokenTimeout(self):
    return self.getAttribute('token')

  def setTokenTimeout(self, val):
    return self.addIntegerAttribute('token', val, (0, None))

  def delTokenTimeout(self):
    return self.removeAttribute('token')

  def getTokenRetransmits(self):
    return self.getAttribute('token_retransmits_before_loss_const')

  def setTokenRetransmits(self, val):
    return self.addIntegerAttribute('token_retransmits_before_loss_const', val, (0, None))

  def delTokenRetransmits(self):
    return self.removeAttribute('token_retransmits_before_loss_const')

  def getConsensusTimeout(self):
    return self.getAttribute('consensus')

  def setConsensusTimeout(self, val):
    return self.addIntegerAttribute('consensus', val, (0, None))

  def delConsensusTimeout(self):
    return self.removeAttribute('consensus')

  def getRRPMode(self):
    return self.getAttribute('rrp_mode')

  def setRRPMode(self, val):
    if not val:
        self.removeAttribute('rrp_mode')
        return None

    val = val.lower()
    if val not in ('active', 'passive', 'none'):
        raise ValueError, val
    self.addAttribute('rrp_mode', val)
    return val

  def delRRPMode(self):
    return self.removeAttribute('rrp_mode')

  def getSecAuth(self):
    return self.getBinaryAttribute('secauth')

  def setSecAuth(self, val):
    return self.addBinaryAttribute('secauth', val, ('0', '1'))

  def delSecAuth(self):
    return self.removeAttribute('secauth')

  def getFailRecvConst(self):
    return self.getAttribute('fail_recv_const')

  def setFailRecvConst(self, val):
    return self.addIntegerAttribute('fail_recv_const', val, (0, None))

  def delFailRecvConst(self):
    return self.removeAttribute('fail_recv_const')

  def getKeyFile(self):
    return self.getAttribute('keyfile')

  def setKeyFile(self, val):
    return self.addAttribute('keyfile', val)

  def delKeyFile(self):
    return self.removeAttribute('keyfile')

  def removeDefaults(self):
    if self.getJoinTimeout() == self.DEFAULTS.get('join'):
        self.delJoinTimeout()
    if self.getTokenTimeout() == self.DEFAULTS.get('token'):
        self.delTokenTimeout()
    if self.getTokenRetransmits() == self.DEFAULTS.get('token_retransmits_before_loss_const'):
        self.delTokenRetransmits()
    if self.getConsensusTimeout() == self.DEFAULTS.get('consensus'):
        self.delConsensusTimeout()
    if self.getSecAuth() == int(self.DEFAULTS.get('secauth')):
        self.delSecAuth()
    if self.getFailRecvConst() == self.DEFAULTS.get('fail_recv_const'):
        self.delFailRecvConst()
    if self.getRRPMode() == self.DEFAULTS.get('rrp_mode'):
        self.delRRPMode()
