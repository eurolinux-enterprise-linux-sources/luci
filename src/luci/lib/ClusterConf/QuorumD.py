# Copyright (C) 2006-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = "quorumd"

class QuorumD(TagObject):
  DEFAULTS = {
    'reboot':           '1',
    'use_uptime':       '1',
    'stop_cman':        '0',
    'io_timeout':       '0',
    'paranoid':         '0',
    'scheduler':        'rr',
    'allow_kill':       '1',
    'upgrade_wait':     '2',
    'max_error_cycles': '0',
    'votes':            None,
  }
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.attr_hash.update(self.DEFAULTS)

  def getVotes(self):
    try:
        return int(self.getAttribute('votes'))
    except:
        pass
    return None

  def setVotes(self, val):
    return self.addIntegerAttribute('votes', val, (1, None))

  def delVotes(self):
    return self.removeAttribute('votes')

  def getInterval(self):
    return self.getAttribute('interval')

  def setInterval(self, val):
    return self.addIntegerAttribute('interval', val, (0, None))

  def delInterval(self):
    return self.removeAttribute('interval')

  def getTKO(self):
    return self.getAttribute('tko')

  def setTKO(self, val):
    return self.addIntegerAttribute('tko', val, (0, None))

  def delTKO(self):
    return self.removeAttribute('tko')

  def getMinScore(self):
    return self.getAttribute('min_score')

  def setMinScore(self, val):
    return self.addIntegerAttribute('min_score', val, (0, None))

  def delMinScore(self):
    return self.removeAttribute('min_score')

  def getDevice(self):
    return self.getAttribute('device')

  def setDevice(self, val):
    return self.addAttribute('device', val)

  def delDevice(self):
    return self.removeAttribute('device')

  def getLabel(self):
    return self.getAttribute('label')

  def setLabel(self, val):
    return self.addAttribute('label', val)

  def getCmanLabel(self):
    return self.getAttribute('cman_label')

  def delLabel(self):
    return self.removeAttribute('label')

  def setCmanLabel(self, val):
    return self.addAttribute('cman_label', val)

  def delCmanLabel(self):
    return self.removeAttribute('cman_label')

  def getStatusFile(self):
    return self.getAttribute('status_file')

  def setStatusFile(self, val):
    return self.addAttribute('status_file', val)

  def delStatusFile(self):
    return self.removeAttribute('status_file')

  def getScheduler(self):
    return self.getAttribute('scheduler')

  def setScheduler(self, val):
    sched = val.lower()
    if not sched in ('rr', 'fifo', 'other'):
        raise ValueError, sched
    return self.addAttribute('scheduler', sched)

  def delScheduler(self):
    return self.removeAttribute('scheduler')

  def getReboot(self):
    return self.getBinaryAttribute('reboot')

  def setReboot(self, val):
    return self.addBinaryAttribute('reboot', val, ('0', '1'))

  def delReboot(self):
    return self.removeAttribute('reboot')

  def getPriority(self):
    return self.getAttribute('priority')

  def setPriority(self, val):
    return self.addIntegerAttribute('priority', val, (-20, 100))

  def delPriority(self):
    return self.removeAttribute('priority')

  def getStopCman(self):
    return self.getBinaryAttribute('stop_cman')

  def setStopCman(self, val):
    return self.addBinaryAttribute('stop_cman', val, ('0', '1'))

  def delStopCman(self):
    return self.removeAttribute('stop_cman')

  def getParanoid(self):
    return self.getBinaryAttribute('paranoid')

  def setParanoid(self, val):
    return self.addBinaryAttribute('paranoid', val, ('0', '1'))

  def delParanoid(self):
    return self.removeAttribute('paranoid')

  def getAllowKill(self):
    return self.getBinaryAttribute('allow_kill')

  def setAllowKill(self, val):
    return self.addBinaryAttribute('allow_kill', val, ('0', '1'))

  def delAllowKill(self):
    return self.removeAttribute('allow_kill')

  def getMaxErrorCycles(self):
    return self.getAttribute('max_error_cycles')

  def setMaxErrorCycles(self, val):
    return self.addIntegerAttribute('max_error_cycles', val, (0, None))

  def delMaxErrorCycles(self):
    return self.removeAttribute('max_error_cycles')

  def getIOTimeout(self):
    return self.getBinaryAttribute('io_timeout')

  def setIOTimeout(self, val):
    return self.addBinaryAttribute('io_timeout', val, ('0', '1'))

  def delIOTimeout(self):
    return self.removeAttribute('io_timeout')

  def getMasterWins(self):
    return self.getBinaryAttribute('master_wins')

  def setMasterWins(self, val):
    return self.addBinaryAttribute('master_wins', val, (None, '1'))

  def delMasterWins(self):
    return self.removeAttribute('master_wins')

  def getTKOUp(self):
    return self.getAttribute('tko_up')

  def setTKOUp(self, val):
    return self.addIntegerAttribute('tko_up', val, (0, None))

  def delTKOUp(self):
    return self.removeAttribute('tko_up')

  def getUpgradeWait(self):
    return self.getAttribute('upgrade_wait')

  def setUpgradeWait(self, val):
    return self.addIntegerAttribute('upgrade_wait', val, (1, None))

  def delUpgradeWait(self):
    return self.removeAttribute('upgrade_wait')

  def getUseUptime(self):
    return self.getBinaryAttribute('use_uptime')

  def setUseUptime(self, val):
    return self.addBinaryAttribute('use_uptime', val, ('0', '1'))

  def delUseUptime(self):
    return self.removeAttribute('use_uptime')

  def getHeuristicsLen(self):
    return len(self.children)

  def removeDefaults(self):
    if self.getReboot() == int(self.DEFAULTS.get('reboot')):
        self.delReboot()
    if self.getUseUptime() == int(self.DEFAULTS.get('use_uptime')):
        self.delUseUptime()
    if self.getStopCman() == int(self.DEFAULTS.get('stop_cman')):
        self.delStopCman()
    if self.getIOTimeout() == int(self.DEFAULTS.get('io_timeout')):
        self.delIOTimeout()
    if self.getParanoid() == int(self.DEFAULTS.get('paranoid')):
        self.delParanoid()
    if self.getAllowKill() == int(self.DEFAULTS.get('allow_kill')):
        self.delAllowKill()
    if self.getScheduler() == self.DEFAULTS.get('scheduler'):
        self.delScheduler()
    if self.getUpgradeWait() == self.DEFAULTS.get('upgrade_wait'):
        self.delUpgradeWait()
    if self.getMaxErrorCycles() == self.DEFAULTS.get('max_error_cycles'):
        self.delMaxErrorCycles()
    if self.getVotes() == self.DEFAULTS.get('votes'):
        self.delVotes()
