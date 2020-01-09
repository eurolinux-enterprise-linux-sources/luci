# Copyright (C) 2006-2012 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from xml.dom import minidom, Node
from TagObject import TagObject
from RefObject import RefObject

import Cluster

# Children of <cluster>
import Cman, Totem, QuorumD, FenceDaemon, FenceXVMd, DLM, GFSControld, \
       Group, Logging, ClusterNodes, FenceDevices, Rm, Clvmd

# Children of <cman>
import Multicast, Altmulticast

# Children of <totem>
import Interface

# Children of <quorumd>
import Heuristic

# Children of <dlm>
import Lockspace

# Children of <lockspace>
import Master

# Children of <logging>
import LoggingDaemon

# Children of <clusternodes>
import ClusterNode

# Children of <clusternode>
import Altname, Fence, Unfence

# Children of <fence>
import Method

# Children of <method>
import Device

# Children of <fencedevices>
import FenceDevice

# Children of <rm>
import FailoverDomains, Events, Resources, Service, Vm

# Children of <failoverdomains>
import FailoverDomain

# Children of <failoverdomain>
import FailoverDomainNode

# Children of <events>
import Event

# Children of <resources> and <service>
import Ip, Script, NFSClient, NFSExport, NFSServer, Fs, Samba, Smb, Apache, Named, \
       DRBD, LVM, MySQL, OpenLDAP, Postgres8, Tomcat5, Tomcat6, \
       SAPDatabase, SAPInstance, SybaseASE, Netfs, Clusterfs, \
       OracleDB, OracleListener, OracleInstance

# Children of resource types
import Action

TAGNAMES = {
    Cluster.TAG_NAME:               Cluster.Cluster,
    Totem.TAG_NAME:                 Totem.Totem,
    Interface.TAG_NAME:             Interface.Interface,
    Cman.TAG_NAME:                  Cman.Cman,
    Multicast.TAG_NAME:             Multicast.Multicast,
    Altmulticast.TAG_NAME:          Altmulticast.Altmulticast,
    Group.TAG_NAME:                 Group.Group,
    Clvmd.TAG_NAME:                 Clvmd.Clvmd,
    GFSControld.TAG_NAME:           GFSControld.GFSControld,
    DLM.TAG_NAME:                   DLM.DLM,
    Lockspace.TAG_NAME:             Lockspace.Lockspace,
    Master.TAG_NAME:                Master.Master,
    ClusterNodes.TAG_NAME:          ClusterNodes.ClusterNodes,
    ClusterNode.TAG_NAME:           ClusterNode.ClusterNode,
    Altname.TAG_NAME:               Altname.Altname,
    Method.TAG_NAME:                Method.Method,
    Fence.TAG_NAME:                 Fence.Fence,
    Device.TAG_NAME:                Device.Device,
    Unfence.TAG_NAME:               Unfence.Unfence,
    FenceDaemon.TAG_NAME:           FenceDaemon.FenceDaemon,
    Logging.TAG_NAME:               Logging.Logging,
    LoggingDaemon.TAG_NAME:         LoggingDaemon.LoggingDaemon,
    FenceDevice.TAG_NAME:           FenceDevice.FenceDevice,
    FenceDevices.TAG_NAME:          FenceDevices.FenceDevices,
    FenceXVMd.TAG_NAME:             FenceXVMd.FenceXVMd,
    FailoverDomains.TAG_NAME:       FailoverDomains.FailoverDomains,
    FailoverDomain.TAG_NAME:        FailoverDomain.FailoverDomain,
    FailoverDomainNode.TAG_NAME:    FailoverDomainNode.FailoverDomainNode,
    Events.TAG_NAME:                Events.Events,
    Event.TAG_NAME:                 Event.Event,
    QuorumD.TAG_NAME:               QuorumD.QuorumD,
    Heuristic.TAG_NAME:             Heuristic.Heuristic,
    Rm.TAG_NAME:                    Rm.Rm,
    Service.TAG_NAME:               Service.Service,
    Vm.TAG_NAME:                    Vm.Vm,
    Resources.TAG_NAME:             Resources.Resources,
    Ip.TAG_NAME:                    Ip.Ip,
    Fs.TAG_NAME:                    Fs.Fs,
    Samba.TAG_NAME:                 Samba.Samba,
    Smb.TAG_NAME:                   Smb.Smb,
    Apache.TAG_NAME:                Apache.Apache,
    Named.TAG_NAME:                 Named.Named,
    DRBD.TAG_NAME:                  DRBD.DRBD,
    LVM.TAG_NAME:                   LVM.LVM,
    MySQL.TAG_NAME:                 MySQL.MySQL,
    OpenLDAP.TAG_NAME:              OpenLDAP.OpenLDAP,
    Postgres8.TAG_NAME:             Postgres8.Postgres8,
    Tomcat5.TAG_NAME:               Tomcat5.Tomcat5,
    Tomcat6.TAG_NAME:               Tomcat6.Tomcat6,
    Clusterfs.TAG_NAME:             Clusterfs.Clusterfs,
    Netfs.TAG_NAME:                 Netfs.Netfs,
    Script.TAG_NAME:                Script.Script,
    NFSExport.TAG_NAME:             NFSExport.NFSExport,
    NFSClient.TAG_NAME:             NFSClient.NFSClient,
    NFSServer.TAG_NAME:             NFSServer.NFSServer,
    SAPDatabase.TAG_NAME:           SAPDatabase.SAPDatabase,
    SAPInstance.TAG_NAME:           SAPInstance.SAPInstance,
    SybaseASE.TAG_NAME:             SybaseASE.SybaseASE,
    OracleDB.TAG_NAME:              OracleDB.OracleDB,
    OracleListener.TAG_NAME:        OracleListener.OracleListener,
    OracleInstance.TAG_NAME:        OracleInstance.OracleInstance,
    Action.TAG_NAME:                Action.Action,
}

import logging
log = logging.getLogger(__name__)

class ModelBuilder:
  def __init__(self, conf_xml_obj, cluster_version=(3, 'Fedora', None)):
    if conf_xml_obj is None:
      raise Exception, 'No cluster configuration'
    self.errors = False
    self.errmsg = []
    self.lock_version = False

    self.cluster_ptr = None
    self.cman_ptr = None
    self.totem_ptr = None
    self.logging_ptr = None
    self.group_ptr = None
    self.clvmd_ptr = None
    self.clusternodes_ptr = None
    self.failoverdomains_ptr = None
    self.fencedevices_ptr = None
    self.resourcemanager_ptr = None
    self.fence_daemon_ptr = None
    self.quorumd_ptr = None
    self.fence_xvmd_ptr = None
    self.dlm_ptr = None
    self.gfscontrold_ptr = None
    self.events_ptr = None
    self.resources_ptr = None
    self.mcast_ptr = None
    self.altmcast_ptr = None
    self.lockspace_ptr = None
    self.unknown_elements = list()
    (self.cluster_version, self.cluster_os, self.os_version) = cluster_version

    self.parent = conf_xml_obj
    self.object_tree = self.buildModel(None)
    self.check_empty_ptrs()
    self.check_fence_daemon()
    self.resolve_fence_instance_types()
    self.purgePCDuplicates()
    self.resolve_references()
    self.check_for_nodeids()

  def has_errors(self):
    return self.errors

  def get_errmsgs(self):
    return self.errmsg

  def getClusterVersion(self):
    return self.cluster_version

  def getClusterOS(self):
    return self.cluster_os

  def getOSVersion(self):
    try:
        return float(self.os_version)
    except:
        pass
    return 0.0

  def buildModel(self, parent_node, parent_object=None):
    if parent_node is None:
      parent_node = self.parent

    comment_nodes = []
    new_object = None

    if parent_node.nodeType == Node.DOCUMENT_NODE:
      for n in parent_node.childNodes:
        if n.nodeType == Node.ELEMENT_NODE:
          parent_node = n
        elif n.nodeType == Node.COMMENT_NODE:
          comment_nodes.append(n)

    if parent_node.nodeType == Node.ELEMENT_NODE:
      unknown_element = False
      try:
        # Create proper type
        new_object = TAGNAMES[parent_node.nodeName]()
      except KeyError, e:
        # This allows for custom tags
        new_object = TagObject(parent_node.nodeName)
        unknown_element = True

      new_object.comments = [c.data for c in comment_nodes]

      for k, v in parent_node.attributes.items():
        new_object.addAttribute(k, v)

      if unknown_element is True:
        self.unknown_elements.append((parent_object, new_object))
        for item in parent_node.childNodes:
          result_object = self.buildModel(item, new_object)
          if result_object is not None:
            new_object.addChild(result_object)
        return None

      if parent_node.nodeName == Cluster.TAG_NAME:
        self.cluster_ptr = new_object
      elif parent_node.nodeName == Cman.TAG_NAME:
        self.cman_ptr = new_object
      elif parent_node.nodeName == Totem.TAG_NAME:
        self.totem_ptr = new_object
      elif parent_node.nodeName == QuorumD.TAG_NAME:
        self.quorumd_ptr = new_object
      elif parent_node.nodeName == FenceDaemon.TAG_NAME:
        self.fence_daemon_ptr = new_object
      elif parent_node.nodeName == FenceXVMd.TAG_NAME:
        self.fence_xvmd_ptr = new_object
      elif parent_node.nodeName == DLM.TAG_NAME:
        self.dlm_ptr = new_object
      elif parent_node.nodeName == GFSControld.TAG_NAME:
        self.gfscontrold_ptr = new_object
      elif parent_node.nodeName == Group.TAG_NAME:
        self.group_ptr = new_object
      elif parent_node.nodeName == Logging.TAG_NAME:
        self.logging_ptr = new_object
      elif parent_node.nodeName == ClusterNodes.TAG_NAME:
        self.clusternodes_ptr = new_object
      elif parent_node.nodeName == Rm.TAG_NAME:
        self.resourcemanager_ptr = new_object
      elif parent_node.nodeName == Clvmd.TAG_NAME:
        self.clvmd_ptr = new_object
      elif parent_node.nodeName == FenceDevices.TAG_NAME:
        self.fencedevices_ptr = new_object
      elif parent_node.nodeName == FailoverDomains.TAG_NAME:
        self.failoverdomains_ptr = new_object
      elif parent_node.nodeName == Resources.TAG_NAME:
        self.resources_ptr = new_object
      elif parent_node.nodeName == Multicast.TAG_NAME:
        self.mcast_ptr = new_object
      elif parent_node.nodeName == Altmulticast.TAG_NAME:
        self.altmcast_ptr = new_object
      elif parent_node.nodeName == Lockspace.TAG_NAME:
        self.lockspace_ptr = new_object
      elif parent_node.nodeName == Events.TAG_NAME:
        self.events_ptr = new_object
    else:
      if parent_node.nodeType in (Node.COMMENT_NODE, Node.TEXT_NODE):
        if parent_node.data and not parent_node.data.isspace():
            return parent_node
      return None

    pending_comments = []
    for item in parent_node.childNodes:
      result_object = self.buildModel(item, new_object)
      if result_object is not None:
        if not issubclass(type(result_object), TagObject):
          if result_object.nodeType == Node.COMMENT_NODE:
            pending_comments.append(result_object.data)
          elif result_object.nodeType == Node.TEXT_NODE:
            if type(new_object) is Event.Event:
              new_object.element_text = result_object.data
        else:
          result_object.comments = pending_comments
          new_object.addChild(result_object)
          pending_comments = []

    if len(pending_comments) > 0:
      new_object.trailing_comments = pending_comments
    return new_object

  def getFenceDeviceByName(self, name):
    device = filter(lambda x: x.getName() == name, self.getFenceDevices())
    num_fdevs = len(device)
    if num_fdevs > 1:
      raise Exception, '%d fence devices named %s exist' % (num_fdevs, name)
    if num_fdevs < 1:
      return None
    return device[0]

  ##Because fence devices are declared in a separate XML section
  ##in conf file, agent types for fence instances must be done in
  ##a separate pass, after the DOM is completely built. This method
  ##sets the agent type for each fence instance.
  def resolve_fence_instance_types(self):
    agent_hash = {}
    for fd in self.getFenceDevices():
      agent = fd.getAgentType()
      if agent is not None:
        try:
          agent_hash[fd.getName()] = agent
        except KeyError, e:
          self.errors = True
          self.errmsg.append('Unknown fence device type: %s' % fd.getName())
        except Exception, e1:
          self.errors = True

    for node in self.getNodes():
      for method in node.getFenceMethods():
        for child in method.getMethodDevices():
          try:
            child.setAgentType(agent_hash[child.getName()])
          except KeyError, e:
            self.errors = True
            self.errmsg.append('Unknown fence device: %s' % child.getName())
          except Exception, e1:
            self.errors = True

  ##This method builds RefObject containers for appropriate
  ##entities after the object tree is built.
  def resolve_references(self):
    reset_list_sentinel = True
    while(reset_list_sentinel is True):
      reset_list_sentinel = False
      resource_children = self.resourcemanager_ptr.getChildren()
      for r_child in resource_children:
        if r_child.getTagName() == Service.TAG_NAME:
         reset_list_sentinel = self.find_references(r_child)
         if reset_list_sentinel is True:
           break

  def find_references(self, entity, parent=None):
    if entity.getAttribute("ref") is not None and entity.isRefObject() is False:
        result = self.transform_reference(entity, parent)
        return result

    for child in entity.getChildren():
        result = self.find_references(child, entity)
        if result is True:
          return result
    return False

  def transform_reference(self, entity, parent):
    result = False
    #This entity has a "ref" attr...need to walk through resources list
    #and look for a match
    recs = self.resources_ptr.getChildren()
    for rec in recs:
      if rec.getTagName() == entity.getTagName():
        if entity.getTagName() == "ip":
          if entity.getAttribute("ref") == rec.getAttribute("address"):
            rf = RefObject(rec)
            kids = entity.getChildren()
            for kid in kids:
              rf.addChild(kid)
            result = True
            break
        else:
          if entity.getAttribute("ref") == rec.getName():
            rf = RefObject(rec)
            kids = entity.getChildren()
            for kid in kids:
              rf.addChild(kid)
            result = True
            break

    if result is False:
      return result

    try:
      entity_attr = entity.getAttributes()
      if entity_attr is not None:
        for i in entity_attr.iterkeys():
          if not rf.attr_hash.has_key(i):
            rf.addAttribute(i, entity_attr[i])
    except:
      pass

    if parent is None:
      # Must be a service
      parent = self.resourcemanager_ptr

    try:
        rf.comments = entity.comments
        rf.trailing_comments = entity.trailing_comments
        rf.element_text = entity.element_text
    except:
        pass

    parent.replaceChild(entity, rf)
    return True

  def lockConfigVersion(self):
    self.lock_version = True
    self.getClusterPtr().is_cfg_version_dirty = True

  def exportModelAsString(self):
    if self.perform_final_check() is False: # failed
      return None

    #check for dual power fences
    self.dual_power_fence_check()
    self.restore_unknown_elements()

    try:
      doc = minidom.Document()
      self.object_tree.generateXML(doc)
      strbuf = doc.toprettyxml()

      ##Need to restore model
      self.parent = doc

      self.object_tree = self.buildModel(None)
      self.check_empty_ptrs()
      self.check_fence_daemon()
      self.resolve_fence_instance_types()
      self.purgePCDuplicates()
      self.resolve_references()
      if self.lock_version is True:
        self.getClusterPtr().is_cfg_version_dirty = True
    except Exception, e:
      strbuf = ""

    return strbuf

  def restore_unknown_elements(self):
    for item in self.unknown_elements:
      duplicate = False
      for kid in item[0].getChildren():
        if kid == item[1]:
          duplicate = True
          break
      if duplicate is not True:
        item[0].addChild(item[1])

  def check_for_nodeids(self):
    for node in self.getNodes():
      if node.getNodeID() is None:
        node.setNodeID(self.getUniqueNodeID())

  def getUniqueNodeID(self):
    nodes = self.getNodes()
    total_nodes = len(nodes)
    dex_list = list()
    for nd_idx in range (1, (total_nodes + 3)):
      dex_list.append(str(nd_idx))

    for dex in dex_list:
      found = False
      for node in nodes:
        ndid = node.getNodeID()
        if ndid is not None:
          if ndid == dex:
            found = True
            break
        else:
          continue

      if found is True:
        continue
      else:
        return dex

  def getNodes(self):
    # Find the clusternodes obj and return clusternode children
    ret = list()
    for i in self.clusternodes_ptr.getChildren():
      if type(i) is not ClusterNode.ClusterNode:
        self.errors = True
        try:
          if not i.errors:
            i.errors = True
            cur_msg = 'Expecting clusternode element, got %s' % i.getTagName()
            self.errmsg.append(cur_msg)
            log.error("Error parsing cluster.conf XML: %s" % cur_msg)
        except:
          pass
      else:
        ret.append(i)
    return ret

  def getNodeNames(self):
    return map(lambda x: x.getName(), self.getNodes())

  def getNodeNameById(self, node_id):
    try:
        return filter(lambda x: x.getNodeID() == node_id, self.getNodes())[0].getName()
    except:
        pass
    return None

  def getNodeByName(self, node_name):
    try:
        return filter(lambda x: x.getName() == node_name, self.getNodes())[0]
    except:
        pass
    return None

  def addNode(self, clusternode):
    self.clusternodes_ptr.addChild(clusternode)

  def deleteNode(self, clusternode):
    #1) delete any non-shared fence devices used by this node
    #2) delete node
    #3) delete failoverdomainnodes with same name

    name = clusternode.getName()

    for method in clusternode.getFenceMethods():
        for fence in method.getMethodDevices():
            fdev = self.getFenceDeviceByName(fence.getName())
            if fdev and not fdev.isShared():
                self.deleteFenceDevice(fdev)

    self.clusternodes_ptr.removeChild(clusternode)

    found_one = True

    while found_one is True:
      found_one = False
      fdoms = self.getFailoverDomains()
      for fdom in fdoms:
        for child in fdom.getFailoverDomainNodes():
          if child.getName() == name:
            fdom.removeChild(child)
            found_one = True
            break

  def retrieveNodeByName(self, name):
    ret = filter(lambda x: x.getName() == name, self.getNodes())
    if len(ret) != 1:
      raise KeyError, name
    return ret[0]

  def deleteNodeByName(self, name):
    return self.deleteNode(self.retrieveNodeByName(name))

  def retrieveServiceByName(self, name):
    svcs = self.getServices()
    for svc in svcs:
      if svc.getName() == name:
        return svc
    return None

  def getServicesForFdom(self, name):
    svc_list = filter(lambda x: x.getFailoverDomain() == name, self.getServices())
    return svc_list

  def retrieveVMsByName(self, name):
    vms = self.getVMs()
    for v in vms:
      if v.getName() == name:
        return v
    return None

  def del_totem(self):
    if self.totem_ptr is not None:
      self.cluster_ptr.removeChild(self.totem_ptr)
      self.totem_ptr = None

  def addTotem(self):
    self.del_totem()
    if self.totem_ptr is None:
        self.totem_ptr = Totem.Totem()
        self.cluster_ptr.addChild(self.totem_ptr)
    return self.totem_ptr
      
  def hasFenceXVM(self):
    return self.fence_xvmd_ptr is not None

  # Right now the fence_xvmd tag is empty, but allow the object
  # to be passed in case attributes are added in the future.
  def addFenceXVM(self, obj):
    if self.fence_xvmd_ptr is not None:
      self.cluster_ptr.removeChild(self.fence_xvmd_ptr)
    self.cluster_ptr.addChild(obj)
    self.fence_xvmd_ptr = obj

  def delFenceXVM(self):
    if self.fence_xvmd_ptr is not None:
      self.cluster_ptr.removeChild(self.fence_xvmd_ptr)
      self.fence_xvmd_ptr = None

  def addFenceDevice(self, device):
    self.fencedevices_ptr.addChild(device)

  def deleteFenceDevice(self, device):
    if self.fencedevices_ptr is None or device is None:
      return False
    self.removeFenceInstancesForFenceDevice(device.getName())
    self.fencedevices_ptr.removeChild(device)
    return True

  def getFenceDevices(self):
    ret = list()
    if self.fencedevices_ptr is None:
      return ret
    else:
      for i in self.fencedevices_ptr.getChildren():
        if type(i) is not FenceDevice.FenceDevice:
          self.errors = True
          try:
            if not i.errors:
              i.errors = True
              cur_msg = 'Expecting fencedevice tag, got %s' % i.getTagName()
              self.errmsg.append(cur_msg)
              log.error("Error parsing cluster.conf XML: %s" % cur_msg)
          except:
              pass
        else:
          ret.append(i)
    return ret

  def getNodesUsingFence(self, fence_name):
    nodes_using = []
    nodes = self.getNodes()
    for i in nodes:
        added_node = False
        methods = i.getFenceMethods()
        for l in methods:
            lc = l.getMethodDevices()
            for dev in lc:
                if dev.getName() == fence_name:
                    nodes_using.append(i)
                    added_node = True
                    break
            if added_node != False:
                break
    return nodes_using

  def getFenceDevicePtr(self):
    return self.fencedevices_ptr

  def getFailoverDomains(self):
    ret = list()
    if self.failoverdomains_ptr is None:
      return ret
    for i in self.failoverdomains_ptr.getChildren():
      if type(i) is not FailoverDomain.FailoverDomain:
        self.errors = True
        try:
          if not i.errors:
            i.errors = True
            cur_msg = 'Expecting failoverdomain element, got %s' % i.getTagName()
            self.errmsg.append(cur_msg)
            log.error("Error parsing cluster.conf XML: %s" % cur_msg)
        except:
          pass
      else:
        ret.append(i)
    return ret

  def getFailoverDomainPtr(self):
    return self.failoverdomains_ptr

  def addFailoverDomain(self, fdom):
    self.failoverdomains_ptr.addChild(fdom)

  def getFailoverDomainByName(self, fdom_name):
    fdoms = self.getFailoverDomains()
    for i in fdoms:
      if i.getName() == fdom_name:
        return i
    return None

  def getFailoverDomainsForNode(self, nodename):
    matches = list()
    faildoms = self.getFailoverDomains()
    for fdom in faildoms:
      for node in fdom.getFailoverDomainNodes():
        if node.getName() == nodename:
          matches.append(fdom)
          break
    return matches

  def addNodeToFailoverDomain(self, node, fd):
    fdoms = self.getFailoverDomains()
    for fdom in fdoms:
      if fdom.getName() == fd:
        kids = fdom.getChildren()
        newnode = FailoverDomainNode.FailoverDomainNode()
        if len(kids) != 0: #Use an existing node as a baseline...
          newnode.attr_hash.update(kids[0].getAttributes())
        newnode.setName(node)
        fdom.addChild(newnode)
        return
    return

  def removeNodeFromFailoverDomain(self, node, fd):
    fdoms = self.getFailoverDomains()
    for fdom in fdoms:
      if fdom.getName() == fd:
        for kid in fdom.getFailoverDomainNodes():
          if kid.getName() == node:
            fdom.removeChild(kid)
            return
    return

  def getMcastPtr(self):
    return self.mcast_ptr

  def addMcastPtr(self):
    if self.mcast_ptr is None:
        self.mcast_ptr = Multicast.Multicast()
        self.cman_ptr.addChild(self.mcast_ptr)
    return self.mcast_ptr

  def getMcastAddr(self):
    if self.mcast_ptr is not None:
        return self.mcast_ptr.getAddr()
    return None

  def getAltmcastPtr(self):
    return self.altmcast_ptr

  def addAltmcastPtr(self):
    if self.altmcast_ptr is None:
        self.altmcast_ptr = Altmulticast.Altmulticast()
        self.cman_ptr.addChild(self.altmcast_ptr)
    return self.altmcast_ptr

  def updateRRPConfig(self):
    if not self.get_cluster_multicast():
      return
    if self.altmcast_ptr is None:
      return

    altmcast_addr = self.altmcast_ptr.getAddr()
    altmcast_port = self.altmcast_ptr.getPort()
    altmcast_ttl = self.altmcast_ptr.getTTL()

    for node in self.getNodes():
      an = node.getAltname()
      if an:
        if altmcast_addr and an.getName() == altmcast_addr:
          an.delName()
        if altmcast_port and an.getPort() == altmcast_port:
          an.delPort()
        if altmcast_ttl and an.getTTL() == altmcast_ttl:
          an.delTTL()
    
  def setQuorumd(self, qd):
    cp = self.getClusterPtr()
    cp.addChild(qd)
    self.quorumd_ptr = qd

  def delQuorumd(self):
    cp = self.getClusterPtr()
    if self.quorumd_ptr is not None:
        cp.removeChild(self.quorumd_ptr)
        self.quorumd_ptr = None

  def delLogging(self):
    cp = self.getClusterPtr()
    if self.logging_ptr is not None:
        cp.removeChild(self.logging_ptr)
        self.logging_ptr = None

  def addLogging(self, obj):
    self.delLogging()
    cp = self.getClusterPtr()
    cp.addChild(obj)
    self.logging_ptr = obj

  def isQuorumd(self):
    return self.quorumd_ptr is not None

  def getQuorumdPtr(self):
    return self.quorumd_ptr

  def check_empty_ptrs(self):
    if self.resourcemanager_ptr is None:
      rm = Rm.Rm()
      self.cluster_ptr.addChild(rm)
      self.resourcemanager_ptr = rm

    if self.cman_ptr is None:
        cman = Cman.Cman()
        self.cluster_ptr.addChild(cman)
        self.cman_ptr = cman

    if self.failoverdomains_ptr is None:
      fdoms = FailoverDomains.FailoverDomains()
      self.resourcemanager_ptr.addChild(fdoms)
      self.failoverdomains_ptr = fdoms

    if self.fencedevices_ptr is None:
      fds = FenceDevices.FenceDevices()
      self.cluster_ptr.addChild(fds)
      self.fencedevices_ptr = fds

    if self.resources_ptr is None:
      rcs = Resources.Resources()
      self.resourcemanager_ptr.addChild(rcs)
      self.resources_ptr = rcs

    if self.fence_daemon_ptr is None:
      fdp = FenceDaemon.FenceDaemon()
      self.cluster_ptr.addChild(fdp)
      self.fence_daemon_ptr = fdp

  def getServices(self):
    rg_list = list()
    if self.resourcemanager_ptr is not None:
      kids = self.resourcemanager_ptr.getChildren()
      for kid in kids:
        if kid.getTagName() in (Service.TAG_NAME, Vm.TAG_NAME):
          rg_list.append(kid)

    return rg_list

  def getService(self, svcname):
    services = self.getServices()
    for service in services:
      if service.getName() == svcname:
        return service

    return None

  def getVMs(self):
    rg_list = list()
    if self.resourcemanager_ptr is not None:
      kids = self.resourcemanager_ptr.getChildren()
      for kid in kids:
        if kid.getTagName() == Vm.TAG_NAME:
          rg_list.append(kid)

    return rg_list

  def deleteFailoverDomain(self, fdom):
    for f in self.getFailoverDomains():
      if f.getName() == fdom:
        self.failoverdomains_ptr.removeChild(f)
        break

  def deleteService(self, service):
    if self.resourcemanager_ptr is not None:
      kids = self.resourcemanager_ptr.getChildren()
      for kid in kids:
        if kid.getName() == service:
          self.resourcemanager_ptr.removeChild(kid)
          break

  def getResources(self):
    if self.resources_ptr is not None:
      return self.resources_ptr.getChildren()
    else:
      return list()

  def getResourcesPtr(self):
    return self.resources_ptr

  def getResourceManagerPtr(self):
    if self.resourcemanager_ptr is None:
        self.addResourceManagerPtr()
    return self.resourcemanager_ptr

  def addResourceManagerPtr(self):
    if self.resourcemanager_ptr is None:
        rm = Rm.Rm()
        self.cluster_ptr.addChild(rm)
        self.resourcemanager_ptr = rm
    return self.resourcemanager_ptr

  def getClvmdPtr(self):
    if self.clvmd_ptr is None:
        self.addClvmdPtr()
    return self.clvmd_ptr

  def addClvmdPtr(self):
    if self.clvmd_ptr is None:
        cobj = Clvmd.Clvmd()
        self.cluster_ptr.addChild(cobj)
        self.clvmd_ptr = cobj
    return self.clvmd_ptr

  def getDLMPtr(self):
    if self.dlm_ptr is None:
        self.addDLMPtr()
    return self.dlm_ptr

  def addDLMPtr(self):
    if self.dlm_ptr is None:
        dobj = DLM.DLM()
        self.cluster_ptr.addChild(dobj)
        self.dlm_ptr = dobj
    return self.dlm_ptr

  def getGFSControldPtr(self):
    if self.gfscontrold_ptr is None:
        self.addGFSControldPtr()
    return self.gfscontrold_ptr

  def addGFSControldPtr(self):
    gobj = GFSControld.GFSControld()
    self.cluster_ptr.addChild(gobj)
    self.gfscontrold_ptr = gobj
    return gobj

  def getGroupPtr(self):
    if self.group_ptr is None:
        self.addGroupPtr()
    return self.group_ptr

  def addGroupPtr(self):
    gobj = Group.Group()
    self.cluster_ptr.addChild(gobj)
    self.group_ptr = gobj
    return gobj

  def getResourceByName(self, name):
    resources = self.resources_ptr.getChildren()
    res = filter(lambda x: x.getName() == name, resources)
    if not res or len(res) < 1:
      raise KeyError, name
    if len(res) > 1:
      raise ValueError, 'More than one resource is named "%s"' % name
    return res[0]

  def deleteResource(self, name):
    for i in self.resources_ptr.getChildren():
      if i.getName() == name:
        self.resources_ptr.removeChild(i)
        return i
    raise KeyError, name

  def getClusterNodesPtr(self):
    return self.clusternodes_ptr

  def getClusterPtr(self):
    return self.cluster_ptr

  def getClusterName(self):
    return self.getClusterPtr().getName()

  def getClusterConfigVersion(self):
    return self.getClusterPtr().getConfigVersion()

  def setClusterConfigVersion(self, version):
    return self.getClusterPtr().setConfigVersion(version)

  def getCMANPtr(self):
    return self.cman_ptr

  def getTotemPtr(self):
    return self.totem_ptr

  def getLoggingPtr(self):
    return self.logging_ptr

  def set_cluster_broadcast(self):
    self.del_cluster_udpu()
    if self.del_cluster_multicast() is False:
      return False
    return self.cman_ptr.setBroadcast(True)

  def del_cluster_broadcast(self):
    if self.cman_ptr is None:
      return False
    self.cman_ptr.delBroadcast()

  def get_cluster_broadcast(self):
    if self.cman_ptr is None:
      return False
    return self.cman_ptr.getBroadcast()

  def del_cluster_multicast(self):
    if self.cman_ptr is None:
      return True

    if self.mcast_ptr is not None:
        self.cman_ptr.removeChild(self.mcast_ptr)
        self.mcast_ptr = None
    if self.altmcast_ptr is not None:
        self.cman_ptr.removeChild(self.altmcast_ptr)
        self.altmcast_ptr = None
    return True

  def set_cluster_multicast(self, mcast_addr=None):
    self.del_cluster_broadcast()
    self.del_cluster_udpu()
    if mcast_addr is not None:
        if self.mcast_ptr is None:
            self.addMcastPtr()
        self.mcast_ptr.setAddr(mcast_addr)
    else:
        if self.mcast_ptr is not None:
            self.mcast_ptr.delAddr()

  def get_cluster_udpu(self):
    if self.cman_ptr is None:
      return False
    return self.cman_ptr.getTransport() == 'udpu'

  def set_cluster_udpu(self):
    self.del_cluster_broadcast()
    self.del_cluster_multicast()
    self.cman_ptr.setTransport('udpu')
    return True

  def del_cluster_udpu(self):
    self.cman_ptr.delTransport()

  def get_cluster_multicast(self):
    if not self.get_cluster_udpu() and not self.get_cluster_broadcast():
      return True
    return False

  def check_fence_daemon(self):
    if self.fence_daemon_ptr is None:
      self.fence_daemon_ptr = FenceDaemon.FenceDaemon()
      self.cluster_ptr.addChild(self.fence_daemon_ptr)

  def getFenceDaemonPtr(self):
    return self.fence_daemon_ptr

  def rectifyNewNodenameWithFaildoms(self, oldname, newname):
    fdoms = self.getFailoverDomains()
    for fdom in fdoms:
      for child in fdom.getFailoverDomainNodes():
        if child.getName().strip() == oldname:
          child.setName(newname)

  ###This method runs through ALL fences (Device objs) and changes name attr
  ###to new name
  def rectifyNewFencedevicenameWithFences(self, oldname, newname):
    nodes = self.getNodes()
    for node in nodes:
      methods = node.getFenceMethods()
      for method in methods:
        fences = method.getMethodDevices()
        for fence in fences:
          if fence.getName() == oldname:
            fence.setName(newname)

  ###Method for removing fence instances if a fence device
  ###has been deleted from the configuration
  def removeFenceInstancesForFenceDevice(self, name):
    nodes = self.getNodes()
    for node in nodes:
      methods = node.getFenceMethods()
      for method in methods:
        fences = method.getMethodDevices()
        kill_list = list()
        for fence in fences:
          if fence.getName() == name:
            kill_list.append(fence)
        for victim in kill_list:
          node.removeFenceInstance(method, victim)

  def removeReferences(self, tagobj):
    self.__removeReferences(tagobj, self.cluster_ptr)

  def __removeReferences(self, tagobj, method):
    for t in method.getChildren()[:]:
      if t.isRefObject():
        if t.getObj() == tagobj:
          method.removeChild(t)
          continue
      self.__removeReferences(tagobj, t)

  def get_expected_votes(self):
    node_votes = 0
    qdisk_votes = 0

    if self.quorumd_ptr is not None:
      try:
        qdisk_votes = int(self.quorumd_ptr.getVotes())
      except:
        qdisk_votes = 0

    for i in self.getNodes():
      try:
        cur_votes = int(i.getVotes())
      except:
        cur_votes = 1
      node_votes += cur_votes

    if qdisk_votes != 0:
        return node_votes + qdisk_votes
    else:
        return 2 * node_votes - 1

  def updateReferences(self):
    self.__updateReferences(self.cluster_ptr)

  def __updateReferences(self, method):
    for t in method.getChildren():
      if t.isRefObject():
        t.setRef(t.getObj().getName())
      self.__updateReferences(t)

  def perform_final_check(self):
    self.check_two_node()
    return True

  def check_two_node(self):
    clusternodes_count = len(self.getNodes())

    if self.isQuorumd():
        self.cman_ptr.delTwoNode()
        self.cman_ptr.setExpectedVotes(max(1, self.get_expected_votes()))
    else:
        if clusternodes_count == 2:
            self.cman_ptr.setTwoNode(True)
            self.cman_ptr.setExpectedVotes(1)
        else:
            self.cman_ptr.delTwoNode()
            self.cman_ptr.delExpectedVotes()

  def dual_power_fence_check(self):
    # if 2 or more power controllers reside in the same fence method,
    # duplicate entries must be made for every controller with an
    # attribute for option set first for off, then for on.

    # for every node:
      # for every fence method:
        # examine every fence
        # If fence is of power type, add to 'found' list for that method
        # If 'found' list is longer than 1, write out extra objs
    for node in self.getNodes():
      for method in node.getFenceMethods():
        pc_list = list()
        for kid in method.getMethodDevices():
          if kid.hasNativeOptionSet() is True:
            continue
          if kid.isPowerController() is True:
            pc_list.append(kid)

        if len(pc_list) > 1:
          # Means we found multiple PCs in the same method
          for fence in pc_list:
            fence.addAttribute("option", "off")
            d = Device.Device()
            d.attr_hash.update(fence.getAttributes())
            d.setAgentType(fence.getAgentType())
            d.addAttribute("option", "on")
            method.addChild(d)

  def purgePCDuplicates(self):
    found_one = True
    while found_one is True:
      found_one = False
      nodes = self.getNodes()
      for node in nodes:
        methods = node.getFenceMethods()
        for method in methods:
          kids = method.getMethodDevices()
          for kid in kids: #kids are actual fence instance objects
            #Need to pass over this device if:
            ##1) It is not a power controller, or
            ##2) It had an initial option attr when the model was constructed
            if not kid.isPowerController():
              continue
            if kid.hasNativeOptionSet():
              continue
            res = kid.getAttribute("option")
            if res is not None:
              if res == "off":
                kid.removeAttribute("option")
              else:
                method.removeChild(kid)
                found_one = True
                break
        if found_one is True:
          break

  def searchObjectTree(self, tagtype):
    objlist = list()
    self.object_tree.searchTree(objlist, tagtype)

    return objlist
