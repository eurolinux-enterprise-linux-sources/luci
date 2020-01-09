# Copyright (C) 2006-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = 'cman'

class Cman(TagObject):
  DEFAULTS = {
    'port':             '5405',
    'transport':        'udp',
    'broadcast':        '0',
    'shutdown_timeout': '5000',
    'quorum_dev_poll':  '10000',
    'ccsd_poll':        '1000',
    'upgrading':        '0',
    'disallowed':       '0',
    'hash_cluster_id':  '0',
    'disable_openais':  '0',
  }
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.attr_hash.update(self.DEFAULTS)

  def setBroadcast(self, val):
    return self.addBinaryAttribute('broadcast', val, (None, 'yes'))

  def getBroadcast(self):
    return self.getBinaryAttribute('broadcast')

  def delBroadcast(self):
    return self.removeAttribute('broadcast')

  def getTwoNode(self):
    return self.getBinaryAttribute('two_node')

  def setTwoNode(self, val):
    return self.addBinaryAttribute('two_node', val, (None, '1'))

  def delTwoNode(self):
    return self.removeAttribute('two_node')

  def getExpectedVotes(self):
    return self.getAttribute('expected_votes')

  def setExpectedVotes(self, val):
    return self.addIntegerAttribute('expected_votes', val, (1, None))

  def delExpectedVotes(self):
    return self.removeAttribute('expected_votes')

  def getUpgrading(self):
    return self.getBinaryAttribute('upgrading')

  def setUpgrading(self, val):
    return self.addBinaryAttribute('upgrading', val, (None, '1'))

  def delUpgrading(self):
    return self.removeAttribute('upgrading')

  def getDisallowed(self):
    return self.getBinaryAttribute('disallowed')

  def setDisallowed(self, val):
    return self.addBinaryAttribute('disallowed', val, (None, '1'))

  def delDisallowed(self):
    return self.removeAttribute('disallowed')

  def getQuorumDevPoll(self):
    return self.getAttribute('quorum_dev_poll')

  def setQuorumDevPoll(self, val):
    return self.addIntegerAttribute('quorum_dev_poll', val, (0, None))

  def delQuorumDevPoll(self):
    return self.removeAttribute('quorum_dev_poll')

  def getShutdownTimeout(self):
    return self.getAttribute('shutdown_timeout')

  def setShutdownTimeout(self, val):
    return self.addIntegerAttribute('shutdown_timeout', val, (0, None))

  def delShutdownTimeout(self):
    return self.removeAttribute('shutdown_timeout')

  def getCcsdPoll(self):
    return self.getAttribute('ccsd_poll')

  def setCcsdPoll(self, val):
    return self.addIntegerAttribute('ccsd_poll', val, (0, None))

  def delCcsdPoll(self):
    return self.removeAttribute('ccsd_poll')

  def getDebugMask(self):
    return self.getAttribute('debug_mask')

  def setDebugMask(self, val):
    return self.addIntegerAttribute('debug_mask', val)

  def delDebugMask(self):
    return self.removeAttribute('debug_mask')

  def getPort(self):
    return self.getAttribute('port')

  def setPort(self, val):
    return self.addIntegerAttribute('port', val, (1, 0xffff))

  def delPort(self):
    return self.removeAttribute('port')

  def getClusterId(self):
    return self.getAttribute('cluster_id')
  
  def setClusterId(self, val):
    return self.addIntegerAttribute('cluster_id', val, (0, None))

  def delClusterId(self):
    return self.removeAttribute('cluster_id')

  def getHashClusterId(self):
    return self.getBinaryAttribute('hash_cluster_id')

  def setHashClusterId(self, val):
    return self.addBinaryAttribute('hash_cluster_id', val, (None, '1'))

  def delHashClusterId(self):
    return self.removeAttribute('hash_cluster_id')

  def getKeyFile(self):
    return self.getAttribute('keyfile')

  def setKeyFile(self, val):
    return self.addAttribute('keyfile', val)

  def delKeyFile(self):
    return self.removeAttribute('keyfile')

  def getDisableOpenAIS(self):
    return self.getBinaryAttribute('disable_openais')

  def setDisableOpenAIS(self, val):
    return self.addBinaryAttribute('disable_openais', val, (None, '1'))

  def delDisableOpenAIS(self):
    return self.removeAttribute('disable_openais')

  def getTransport(self):
    return self.getAttribute('transport')

  def delTransport(self):
    return self.removeAttribute('transport')

  def setTransport(self, val):
    if not val:
        return self.delTransport()
    val = val.lower()
    if not val in ('udp', 'udpb', 'udpu', 'rdma'):
        raise Exception, "Invalid transport: %s" % val
    return self.addAttribute('transport', val)

  def removeDefaults(self):
    if self.getPort() == self.DEFAULTS.get('port'):
        self.delPort()
    if self.getTransport() == self.DEFAULTS.get('transport'):
        self.delTransport()
    if self.getQuorumDevPoll() == self.DEFAULTS.get('quorum_dev_poll'):
        self.delQuorumDevPoll()
    if self.getShutdownTimeout() == self.DEFAULTS.get('shutdown_timeout'):
        self.delShutdownTimeout()
    if self.getCcsdPoll() == self.DEFAULTS.get('ccsd_poll'):
        self.delCcsdPoll()
    if self.getBroadcast() == int(self.DEFAULTS.get('broadcast')):
        self.delBroadcast()
    if self.getUpgrading() == int(self.DEFAULTS.get('upgrading')):
        self.delUpgrading()
    if self.getDisallowed() == int(self.DEFAULTS.get('disallowed')):
        self.delDisallowed()
    if self.getHashClusterId() == int(self.DEFAULTS.get('hash_cluster_id')):
        self.delHashClusterId()
    if self.getDisableOpenAIS() == int(self.DEFAULTS.get('disable_openais')):
        self.delDisableOpenAIS()
