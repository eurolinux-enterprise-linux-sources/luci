# Copyright (C) 2006-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from TagObject import TagObject

TAG_NAME = "cluster"

class Cluster(TagObject):
  def __init__(self):
    TagObject.__init__(self)
    self.TAG_NAME = TAG_NAME
    self.is_cfg_version_dirty = False

  def getConfigVersion(self):
    return self.getAttribute('config_version')

  def setConfigVersion(self, version):
    current_version = int(self.getConfigVersion())
    new_version = int(version)

    if new_version < current_version:
        raise ValueError, version
    elif new_version != current_version:
        self.addAttribute("config_version", version)
        self.is_cfg_version_dirty = True
    return new_version

  def incrementConfigVersion(self):
    try:
      version = int(self.getConfigVersion())
    except:
      return None
    return self.setConfigVersion(version + 1)

  def doesClusterUseQuorumDisk(self):
    """Returns a pair (A, B) describing Quorum Disk situation within cluster.

    A ... whether 'quorumd' xml-node present in cluster.conf
    B ... whether all nodes within cluster have either 'votes' attribute equal to '1'
          or no such attribute (which defaults to '1' automatically)

    """
    clusternodes_ptr = None
    qdisk_found = False
    kids = self.getChildren()
    for kid in kids:
      kid_tag_name = kid.getTagName()
      qdisk_found = qdisk_found or (kid_tag_name == "quorumd")
      if kid_tag_name == "clusternodes":
        clusternodes_ptr = kid
        if qdisk_found:
            break
    if clusternodes_ptr == None:
        return qdisk_found, True
    else:
        qdisk_supported = True
        for kid in clusternodes_ptr.getChildren():
            if kid.getTagName() == 'clusternode' and kid.getVotes() != None:
                qdisk_supported = qdisk_supported and kid.getVotes() == '1'
        return qdisk_found, qdisk_supported

  def generateXML(self, doc, parent=None):
    if self.is_cfg_version_dirty is False:
      self.incrementConfigVersion()
    else:
      self.is_cfg_version_dirty = False
    super(Cluster, self).generateXML(doc, parent)
