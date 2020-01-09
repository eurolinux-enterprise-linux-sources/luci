# Copyright (C) 2006-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = "fence_daemon"

class FenceDaemon(TagObject):
  DEFAULTS = {
    'post_join_delay':      '3',
    'post_fail_delay':      '0',
    'override_path':        '/var/run/cluster/fenced_override',
    'override_time':        '3',
    'clean_start':          '0',
    'skip_undefined':       '0',
  }
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.attr_hash.update(self.DEFAULTS)

  def getPostJoinDelay(self):
    return self.getAttribute('post_join_delay')

  def setPostJoinDelay(self, delay):
    return self.addIntegerAttribute('post_join_delay', delay, (0, None))

  def delPostJoinDelay(self):
    return self.removeAttribute('post_join_delay')

  def getPostFailDelay(self):
    return self.getAttribute('post_fail_delay')

  def setPostFailDelay(self, delay):
    return self.addIntegerAttribute('post_fail_delay', delay, (0, None))

  def delPostFailDelay(self):
    return self.removeAttribute('post_fail_delay')

  def getCleanStart(self):
    return self.getBinaryAttribute('clean_start')

  def setCleanStart(self, val):
    return self.addBinaryAttribute('clean_start', val, (None, '1'))

  def delCleanStart(self):
    return self.removeAttribute('clean_start')

  def getSkipUndefined(self):
    return self.getBinaryAttribute('skip_undefined')

  def setSkipUndefined(self, val):
    return self.addBinaryAttribute('skip_undefined', val, (None, '1'))

  def delSkipUndefined(self):
    return self.removeAttribute('skip_undefined')

  def getOverridePath(self):
    return self.getAttribute('override_path')

  def setOverridePath(self, val):
    return self.addAttribute('override_path', val)

  def delOverridePath(self):
    return self.removeAttribute('override_path')

  def getOverrideTime(self):
    return self.getAttribute('override_time')

  def setOverrideTime(self, val):
    return self.addIntegerAttribute('override_time', val, (0, None))

  def delOverrideTime(self):
    return self.removeAttribute('override_time')

  def removeDefaults(self):
    if self.getPostFailDelay() == self.DEFAULTS.get('post_fail_delay'):
        self.delPostFailDelay()
    if self.getPostJoinDelay() == self.DEFAULTS.get('post_join_delay'):
        self.delPostJoinDelay()
    if self.getOverridePath() == self.DEFAULTS.get('override_path'):
        self.delOverridePath()
    if self.getOverrideTime() == self.DEFAULTS.get('override_time'):
        self.delOverrideTime()
    if self.getSkipUndefined() == int(self.DEFAULTS.get('skip_undefined')):
        self.delSkipUndefined()
    if self.getCleanStart() == int(self.DEFAULTS.get('clean_start')):
        self.delCleanStart()
