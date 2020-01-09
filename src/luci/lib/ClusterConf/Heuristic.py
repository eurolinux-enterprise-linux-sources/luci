# Copyright (C) 2006-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = "heuristic"

class Heuristic(TagObject):
  DEFAULTS = {
    'interval':     '2',
    'score':        '1',
  }
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.attr_hash.update(self.DEFAULTS)

  def getProgram(self):
    return self.getAttribute('program')

  def setProgram(self, program):
    return self.addAttribute('program', program)

  def getScore(self):
    return self.getAttribute('score')

  def setScore(self, score):
    return self.addIntegerAttribute('score', score, (1, None))

  def delScore(self):
    return self.removeAttribute('score')

  def getInterval(self):
    return self.getAttribute('interval')

  def setInterval(self, interval):
    return self.addIntegerAttribute('interval', interval, (1, None))

  def delInterval(self):
    return self.removeAttribute('interval')

  def getTKO(self):
    return self.getAttribute('tko')

  def setTKO(self, tko):
    return self.addIntegerAttribute('tko', tko, (0, None))

  def delTKO(self):
    return self.removeAttribute('tko')

  def removeDefaults(self):
    if self.getScore() == self.DEFAULTS.get('score'):
        self.delScore()
    if self.getInterval() == self.DEFAULTS.get('interval'):
        self.delInterval()
    if self.getTKO() == self.DEFAULTS.get('tko'):
        self.delTKO()
