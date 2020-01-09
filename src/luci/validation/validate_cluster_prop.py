# Copyright (C) 2009-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from luci.lib.helpers import ugettext as _

from luci.lib.ClusterConf.FailoverDomain import FailoverDomain
from luci.lib.ClusterConf.FailoverDomainNode import FailoverDomainNode
from luci.lib.ClusterConf.QuorumD import QuorumD
from luci.lib.ClusterConf.Heuristic import Heuristic
from luci.lib.ClusterConf.Method import Method
from luci.lib.ClusterConf.Logging import Logging
from luci.lib.ClusterConf.LoggingDaemon import LoggingDaemon
from luci.lib.ClusterConf.Altname import Altname 

from luci.lib.db_helpers import create_cluster_obj, get_node_by_name, get_cluster_db_obj, create_user_db_obj
from luci.lib.ricci_communicator import RicciCommunicator
from luci.lib.ricci_helpers import send_batch_parallel

from luci.model import DBSession
from luci.model.auth import User, Group

from validate_fence import validateFenceDevice, validateNewFenceDevice, validate_fenceinstance

from xml.dom import minidom

import logging
log = logging.getLogger(__name__)

def validate_fdom_prop_form(model, **kw):
    errors = []

    fdom_name = kw.get('name')
    if not fdom_name or fdom_name.isspace():
        return (False, {'errors': _('No failover domain name was given')})
    fdom = model.getFailoverDomainByName(fdom_name)
    if not fdom:
        return (False, {'errors': _('No failover domain named "%s" exists') % fdom_name})

    fdom.setOrdered(kw.get('ordered') is not None)
    fdom.setRestricted(kw.get('restricted') is not None)
    fdom.setNoFailback(kw.get('nofailback') is not None)
    return (len(errors) < 1, {'errors': errors})

def validate_fdom_create_form(model, **kw):
    errors = []

    fdom_name = kw.get('fdom_name')
    if not fdom_name or fdom_name.isspace():
        errors.append(_('No name was given for this failover domain'))
        return (False, {'errors': errors})

    if model.getFailoverDomainByName(fdom_name):
        errors.append(_('A failover domain named "%s" already exists') % fdom_name)
        return (False, {'errors': errors})

    fdom = FailoverDomain()
    fdom.setName(fdom_name)

    ordered = kw.get('ordered') is not None
    fdom.setOrdered(ordered)
    fdom.setRestricted(kw.get('restricted') is not None)
    fdom.setNoFailback(kw.get('nofailback') is not None)

    for i in model.getNodeNames():
        if kw.get('%s.check' % i):
            fdn = FailoverDomainNode()
            if ordered:
                priority = kw.get('%s.priority' % i)
                if priority and not priority.isspace():
                    try:
                        fdn.setPriority(priority)
                    except:
                        errors.append(_('Invalid priority for failover domain member %s: %s') % (i, priority))
            fdn.setName(i)
            fdom.addChild(fdn)

    model.addFailoverDomain(fdom)
    return (len(errors) < 1, {'errors': errors})

def validate_fdom_prop_settings_form(model, **kw):
    errors = []

    fdom_name = kw.get('name')
    if not fdom_name or fdom_name.isspace():
        return (False, {'errors': _('No failover domain name was given')})
    fdom = model.getFailoverDomainByName(fdom_name)
    if not fdom:
        return (False, {'errors': _('No failover domain named "%s" exists') % fdom_name})

    restricted = fdom.getRestricted()
    ordered = fdom.getOrdered()

    for i in model.getNodeNames():
        fdn = fdom.get_member_node(i)
        if kw.get('%s.check' % i):
            if not fdn:
                fdn = FailoverDomainNode()
                fdn.setName(i)
                fdom.addChild(fdn)

            if ordered:
                priority = kw.get('%s.priority' % i)
                if priority and not priority.isspace():
                    try:
                        fdn.setPriority(priority)
                    except:
                        errors.append(_('Invalid priority for failover domain member %s: %s') % (i, priority))
                else:
                    fdn.delPriority()
            else:
                fdn.delPriority()
        else:
            if fdn:
                fdom.removeChild(fdn)

    return (len(errors) < 1, {'errors': errors})

def validate_add_existing(**kw):
    errors = []

    cluster_name = kw.get('clustername')
    num_nodes = kw.get('num_nodes')
    all_passwd_same = kw.get('allSameCheckBox') is not None

    if not cluster_name:
        errors.append(_("No cluster name was given"))

    db_obj = get_cluster_db_obj(cluster_name)
    if db_obj is not None:
        errors.append(_('A cluster named "%s" has already been added') % cluster_name)

    if not num_nodes:
        errors.append(_("The number of cluster nodes was not given"))
    else:
        try:
            num_nodes = int(num_nodes)
        except ValueError:
            errors.append(_("An invalid number of cluster nodes was given: %s")
                % num_nodes)

    if len(errors) != 0:
        return (False, {'errors': errors })

    node_triples = []
    node_list = []

    first_passwd = None
    if all_passwd_same is True:
        for i in xrange(num_nodes):
            cur_passwd = kw.get('node%d_passwd' % i)
            if cur_passwd and not cur_passwd.isspace():
                first_passwd = cur_passwd
                break

    for i in xrange(num_nodes):
        nodename = kw.get('node%d_host' % i)
        if not nodename:
            errors.append(_("No nodename was given for node %d") % i)
            continue

        ricci_host = kw.get('node%d_riccihost' % i)
        if not ricci_host:
            ricci_host = nodename 

        ricci_port = kw.get('node%d_port' % i)
        if not ricci_port:
            errors.append(_("No port was given for node %s") % nodename)
        else:
            try:
                ricci_port = int(ricci_port)
                if ricci_port != ricci_port & 0xffff:
                    raise ValueError, ricci_port
            except ValueError:
                errors.append(_("An invalid port was given for node %s: %s")
                    % (nodename, kw.get('node%d_port' % i)))

        node_pass = kw.get('node%d_passwd' % i)
        if not node_pass:
            if all_passwd_same and first_passwd is not None:
                node_pass = first_passwd
            else:
                errors.append(_("No password was given for node %s") % nodename)

        node_triples.append(((ricci_host, ricci_port), RicciCommunicator.auth, [ node_pass ]))
        node_list.append((nodename, ricci_host, ricci_port))

    ret = send_batch_parallel(node_triples, 10)

    if len(errors) != 0:
        return (False, {'errors': errors })

    if create_cluster_obj(cluster_name, node_list) is not True:
        errors.append(_('Unable to create the database objects for cluster %s') % cluster_name)
    else:
        return (True, {'flash': [ _('Cluster "%s" was successfully added to luci') % cluster_name ]})
    return (len(errors) < 1, {'errors': errors})

def validate_qdisk_config(model, **kw):
    errors = []

    qdisk_found, qdisk_supported = model.getClusterPtr().doesClusterUseQuorumDisk()
    qdp = model.getQuorumdPtr()

    use_qdisk = None
    quorumd = kw.get('quorumd')
    if quorumd == 'true':
        use_qdisk = True
    elif quorumd == 'false':
        use_qdisk = False

    if use_qdisk is None:
        return (False, {'errors': [  _('No qdisk value was given') ] })

    if use_qdisk is False:
        if qdp is not None:
            model.delQuorumd()
            return (True, {'flash': [ _('The updated quorum disk settings will not take effect until the cluster is restarted') ] })
        # No changes
        return (False, {'errors': [ _('No changes were made to the quorum disk settings') ] })
    elif qdisk_supported is not True:
        return (False, {'errors': [ _('Quorum Disk cannot be used unless each cluster node has exactly 1 vote') ] })

    qd = QuorumD()
    if qdp is not None:
        qd.getAttributes().update(qdp.getAttributes())
        model.delQuorumd()

    min_score = kw.get('min_score')
    if min_score and not min_score.isspace():
        try:
            qd.setMinScore(min_score)
        except:
            errors.append(_('An invalid qdisk minimum score value was given: %s') % min_score)
    else:
        qd.delMinScore()

    device = kw.get('device')
    label = kw.get('label')

    if not device and not label:
        errors.append(_('Neither a qdisk device nor label was given'))
    if device and label:
        errors.append(_('You may give either a qdisk device or label, but not both'))

    if device:
        qd.delLabel()
        qd.setDevice(device)
    else:
        qd.delDevice()
        qd.setLabel(label)

    heuristic_scores = 0
    for i in xrange(10):
        qheur = Heuristic()
        hprog = kw.get('heuristic%d:hprog' % i)
        hinterval = kw.get('heuristic%d:hinterval' % i)
        hscore = kw.get('heuristic%d:hscore' % i)
        htko = kw.get('heuristic%d:htko' % i)

        if not hprog and not hinterval and not hscore and not htko:
            continue

        if not hprog:
            errors.append(_('No qdisk program given for heuristic %d')
                % (i + 1))

        qheur.setProgram(hprog)

        if hinterval:
            try:
                qheur.setInterval(hinterval)
            except:
                errors.append(_('Invalid qdisk interval given for heuristic %d: %s')
                    % (i + 1, hinterval))

        if hscore:
            try:
                qheur.setScore(hscore)
            except:
                errors.append(_('Invalid qdisk score given for heuristic %d: %s')
                    % (i + 1, hscore))

        heuristic_scores += int(qheur.getScore())

        if htko and model.getClusterVersion() >= 3:
            try:
                qheur.setTKO(htko)
            except:
                errors.append(_('Invalid qdisk TKO value given for heuristic %d: %s') % (i + 1, htko))

        qd.addChild(qheur)

    min_score = qd.getMinScore()
    if min_score and int(min_score) > heuristic_scores:
        errors.append(_('Minimum total score must not exceed the sum of the heuristic scores'))

    if kw.get('expert_mode'):
        interval = kw.get('interval')
        if interval and not interval.isspace():
            try:
                qd.setInterval(interval)
            except:
                errors.append(_('An invalid qdisk interval value was given: %s') % interval)
        else:
            qd.delInterval()

        votes = kw.get('votes')
        if votes and not votes.isspace():
            try:
                qd.setVotes(votes)
            except:
                errors.append(_('An invalid qdisk votes value was given: %s') % votes)
        else:
            qd.delVotes()

        tko = kw.get('tko')
        if tko and not tko.isspace():
            try:
                qd.setTKO(tko)
            except:
                errors.append(_('An invalid qdisk TKO value was given: %s') % tko)
        else:
            qd.delTKO()

        cman_label = kw.get('cman_label')
        if cman_label and not cman_label.isspace():
            try:
                qd.setCmanLabel(cman_label)
            except:
                errors.append(_('An invalid value for CMAN label was given: %s') % cman_label)
        else:
            qd.delCmanLabel()

        status_file = kw.get('status_file')
        if status_file and not status_file.isspace():
            try:
                qd.setStatusFile(status_file)
            except:
                errors.append(_('An invalid value for status file was given: %s') % status_file)
        else:
            qd.delStatusFile()

        tko_up = kw.get('tko_up')
        if tko_up and not tko_up.isspace():
            try:
                qd.setTKOUp(tko_up)
            except:
                errors.append(_('An invalid value for TKO Up was given: %s') % tko_up)
        else:
            qd.delTKOUp()

        max_error_cycles = kw.get('max_error_cycles')
        if max_error_cycles and not max_error_cycles.isspace():
            try:
                qd.setMaxErrorCycles(max_error_cycles)
            except:
                errors.append(_('An invalid value for Max Error Cycles was given: %s') % max_error_cycles)
        else:
            qd.delMaxErrorCycles()

        upgrade_wait = kw.get('upgrade_wait')
        if upgrade_wait and not upgrade_wait.isspace():
            try:
                qd.setUpgradeWait(upgrade_wait)
            except:
                errors.append(_('An invalid value for Upgrade Wait was given: %s') % upgrade_wait)
        else:
            qd.delUpgradeWait()

        scheduler = kw.get('scheduler')
        if scheduler and not scheduler.isspace():
            try:
                qd.setScheduler(scheduler)
            except:
                errors.append(_('An invalid value for scheduler was given: %s') % scheduler)
        else:
            qd.delScheduler()

        priority = kw.get('priority')
        if priority and not priority.isspace():
            try:
                qd.setPriority(priority)
            except:
                errors.append(_('An invalid value for scheduler priority was given: %s') % priority)
        else:
            qd.delPriority()

        qd.setReboot(kw.get('reboot') is not None)
        qd.setUseUptime(kw.get('use_uptime') is not None)
        qd.setStopCman(kw.get('stop_cman') is not None)
        qd.setParanoid(kw.get('paranoid') is not None)
        qd.setIOTimeout(kw.get('io_timeout') is not None)
        qd.setAllowKill(kw.get('allow_kill') is not None)
        qd.setMasterWins(kw.get('master_wins') is not None)

    if len(errors) > 0:
        return (False, {'errors': errors })

    ret = (len(errors) < 1, {'errors': errors})
    if qdp is None:
        ret[1]['start_qdisk'] = True
    model.setQuorumd(qd)
    return ret

def validate_logging_config(obj, prefix, **kw):
    errors = []

    if type(obj) is LoggingDaemon:
        subsys = kw.get('%s_subsys' % prefix)
        if subsys:
            obj.setSubsys(subsys)

    syslog_facility = kw.get('%s_syslog_facility' % prefix)
    if syslog_facility:
        try:
            obj.setSyslogFacility(syslog_facility)
        except:
            errors.append(_('Invalid syslog facility: %s') % syslog_facility)
    else:
        obj.delSyslogFacility()

    syslog_priority = kw.get('%s_syslog_priority' % prefix)
    if syslog_priority:
        try:
            obj.setSyslogPriority(syslog_priority)
        except:
            errors.append(_('Invalid syslog priority: %s') % syslog_priority)
    else:
        obj.delSyslogPriority()

    to_syslog = kw.get('%s_to_syslog' % prefix)
    if not to_syslog:
        obj.delSyslogPriority()
        obj.delSyslogFacility()
        obj.setSyslog(False)
    else:
        obj.setSyslog(True)

    logfile = kw.get('%s_logfile' % prefix)
    if not logfile or logfile.isspace():
        logfile = None
        obj.delLogfilePath()
    else:
        obj.setLogfilePath(logfile)

    logfile_priority = kw.get('%s_logfile_priority' % prefix)
    if logfile_priority:
        try:
            obj.setLogfilePriority(logfile_priority)
        except:
            errors.append(_('Invalid log file priority: %s') % logfile_priority)
    else:
        obj.delLogfilePriority()

    to_logfile = kw.get('%s_to_logfile' % prefix)
    if not to_logfile:
        obj.delLogfilePath()
        obj.delLogfilePriority()
        obj.setLogfile(False)
    else:
        obj.setLogfile(True)

    debug = kw.get('%s_debug' % prefix)
    if not debug:
        obj.delDebug()
    else:
        obj.setDebug(True)

    return obj, errors

def validate_fenced_config(model, **kw):
    from luci.lib.ClusterConf.FenceXVMd import FenceXVMd
    errors = []

    fd = model.getFenceDaemonPtr()

    post_fail_delay = kw.get('post_fail_delay')
    if post_fail_delay and not post_fail_delay.isspace():
        try:
            fd.setPostFailDelay(post_fail_delay)
        except:
            errors.append(_('Invalid post fail delay: %s') % post_fail_delay)
    else:
        fd.delPostFailDelay()

    post_join_delay = kw.get('post_join_delay')
    if post_join_delay and not post_join_delay.isspace():
        try:
            fd.setPostJoinDelay(post_join_delay)
        except:
           errors.append(_('Invalid post join delay: %s') % post_join_delay)
    else:
        fd.delPostJoinDelay()

    if model.getClusterVersion() == 2:
        fence_xvmd = kw.get('fence_xvmd')
        if not fence_xvmd:
            model.delFenceXVM()
        else:
            xvm_obj = FenceXVMd()
            model.addFenceXVM(xvm_obj)

    if kw.get('expert_mode'):
        # Fields only exposed when in "expert mode"
        fd.setCleanStart(kw.get('clean_start') is not None)
        fd.setSkipUndefined(kw.get('skip_undefined') is not None)

        override_path = kw.get('override_path')
        if not override_path or override_path.isspace():
            fd.delOverridePath()
        else:
            fd.setOverridePath(override_path)

        override_time = kw.get('override_time')
        if not override_time or override_time.isspace():
            fd.delOverrideTime()
        else:
            try:
                fd.setOverrideTime(override_time)
            except:
                errors.append(_('Invalid value given for override time: %s') % override_time)

    return (len(errors) < 1, {'errors': errors})

def validate_network_config(model, **kw):
    errors = []
    uses_mcast = True

    multicast = kw.get('multicast')
    mcast_addr = kw.get('mcast_address')

    if multicast == "multicast":
        model.set_cluster_multicast()
    elif multicast == "multicast_manual":
        model.set_cluster_multicast(mcast_addr)
    elif multicast == "broadcast":
        model.set_cluster_broadcast()
        uses_mcast = False
    elif multicast == "udpu":
        model.set_cluster_udpu()
        uses_mcast = False
    else:
        return (False, {'errors': [ _('Invalid value for multicast configuration: %s') % multicast]})

    if not kw.get('expert_mode'):
        return (True, {})

    # The rest of the fields can be set only in expert mode
    totem = model.getTotemPtr()
    if totem is None:
        totem = model.addTotem()

    mcast_ttl = kw.get('ttl')
    mcast_ptr = model.getMcastPtr()
    if uses_mcast is True and mcast_ttl and not mcast_ttl.isspace():
        try:
            if not mcast_ptr:
                mcast_ptr = model.addMcastPtr()
            mcast_ptr.setTTL(mcast_ttl)
        except:
            errors.append(_('Invalid multicast packet TTL: %s') % mcast_ttl)
    else:
        if mcast_ptr:
            mcast_ptr.delTTL()

    join_timeout = kw.get('join_timeout')
    if join_timeout and not join_timeout.isspace():
        try:
            totem.setJoinTimeout(join_timeout)
        except:
            errors.append(_('Invalid value for totem join timeout : %s') % join_timeout)
    else:
        totem.delJoinTimeout()

    token_timeout = kw.get('token_timeout')
    if token_timeout and not join_timeout.isspace():
        try:
            totem.setTokenTimeout(token_timeout)
        except:
            errors.append(_('Invalid value for totem token timeout : %s') % token_timeout)
    else:
        totem.delTokenTimeout()

    token_retransmits = kw.get('token_retransmits')
    if token_retransmits:
        try:
            totem.setTokenRetransmits(token_retransmits)
        except:
            errors.append(_('Invalid value for totem token retransmits before loss: %s') % token_retransmits)
    else:
        totem.delTokenRetransmits()

    consensus_timeout = kw.get('consensus_timeout')
    if consensus_timeout:
        try:
            totem.setConsensusTimeout(consensus_timeout)
        except:
            errors.append(_('Invalid value for totem consensus timeout: %s') % consensus_timeout)
    else:
        totem.delConsensusTimeout()

    token_retransmits_before_loss_const = kw.get('token_retransmits_before_loss_const')
    if token_retransmits_before_loss_const and not token_retransmits_before_loss_const.isspace():
        try:
            totem.setTokenRetransmits(token_retransmits_before_loss_const)
        except:
            errors.append(_('Invalid value for token retransmits before loss constant: %s') % token_retransmits_before_loss_const)
    else:
        totem.delTokenRetransmits()

    fail_recv_const = kw.get('fail_recv_const')
    if fail_recv_const and not fail_recv_const.isspace():
        try:
            totem.setFailRecvConst(fail_recv_const)
        except:
            errors.append(_('Invalid value for failure to receive constant: %s') % fail_recv_const)
    else:
        totem.delFailRecvConst()

    totem.setSecAuth(kw.get('secauth') is not None)
    return (len(errors) < 1, {'errors': errors})

def validate_rrp_config(model, **kw):
    errors = []

    altmcast_ptr = model.getAltmcastPtr()
    if not altmcast_ptr:
        altmcast_ptr = model.addAltmcastPtr()

    altmcast_addr = kw.get('altmcast_addr')
    if altmcast_addr and not altmcast_addr.isspace():
        try:
            altmcast_ptr.setAddr(altmcast_addr)
        except:
            errors.append(_('Invalid alternate ring multicast address: %s') % altmcast_addr)
    else:
        altmcast_ptr.delAddr()

    altmcast_port = kw.get('altmcast_port')
    if altmcast_port and not altmcast_port.isspace():
        try:
            altmcast_ptr.setPort(altmcast_port)
        except:
            errors.append(_('Invalid alternate ring CMAN port: %s') % altmcast_port)
    else:
        altmcast_ptr.delPort()

    altmcast_ttl = kw.get('altmcast_ttl')
    if altmcast_ttl and not altmcast_ttl.isspace():
        try:
            altmcast_ptr.setTTL(altmcast_ttl)
        except:
            errors.append(_('Invalid alternate ring multicast packet TTL: %s') % altmcast_ttl)
    else:
        altmcast_ptr.delTTL()

    for i in model.getNodes():
        cur_node_conf = kw.get('altmcast_%s' % i.getName())
        if cur_node_conf:
            # Since we only want the addr attribute, create a new object
            # to replace an existing altname that may contain old-style config
            try:
                cur_an = Altname()
                cur_an.setName(cur_node_conf)
                i.setAltname(cur_an)
            except Exception, e:
                errors.append(_('Error setting alternate address for %s: %s')
                    % (i.getName(), str(e)))

    # Clean up any old-style config that may still be around
    model.updateRRPConfig()
    return (len(errors) < 1, {'errors': errors})

def validate_log_config(model, **kw):
    new_conf = False

    logobj = model.getLoggingPtr()
    if not logobj:
        logobj = Logging()
        new_conf = True

    ret, errors = validate_logging_config(logobj, 'global', **kw)
    if ret is not None and new_conf is True:
        model.addLogging(logobj)

    for ld in ('rgmanager', 'qdiskd', 'corosync', 'fenced', 'groupd', 'dlm_controld', 'gfs_controld'):
        new_ld = False
        ldobj = None

        if new_conf is False:
            ldobj = logobj.getDaemonConfig(ld)
        if ldobj is None:
            ldobj = LoggingDaemon()
            ldobj.setName(ld)
            new_ld = True

        ret, cur_errors = validate_logging_config(ldobj, ld, **kw)
        errors.extend(cur_errors)
        if ret is not None:
            logobj.setDaemonConfig(ldobj)
        elif new_ld is False:
            logobj.delDaemonConfig(ld)

    for csubsys in ('CLM', 'CPG', 'MAIN', 'SERV', 'CMAN', 'TOTEM', 'QUORUM', 'CONFDB', 'CKPT', 'EVT'):
        new_subsys = False
        csubsys_obj = None

        if new_conf is False:
            csubsys_obj = logobj.getCorosyncSubsysConfig(csubsys)
        if csubsys_obj is None:
            csubsys_obj = LoggingDaemon()
            csubsys_obj.setName('corosync')
            csubsys_obj.setSubsys(csubsys)
            new_subsys = True

        ret, cur_errors = validate_logging_config(csubsys_obj, 'corosync_%s' % csubsys, **kw)
        errors.extend(cur_errors)
        if ret is not None:
            logobj.setCorosyncSubsysConfig(csubsys_obj)
        elif new_subsys is False:
            logobj.delCorosyncSubsysConfig(csubsys)
    return (len(errors) < 1, {'errors': errors})

def validate_general_config(model, **kw):
    errors = []

    config_version = kw.get('config_version')
    if config_version:
        try:
            cur_version = int(model.getClusterConfigVersion())
            config_version = int(config_version)
            if config_version < cur_version:
                return (False, {'errors': [ _('The cluster configuration version entered must be greater than the current version (%d)') % cur_version ]})
            model.setClusterConfigVersion(config_version)
        except:
            return (False, {'errors': [ _('Invalid value for configuration version: %s') % kw.get('config_version') ]})
    return (len(errors) < 1, {'errors': errors})

def validate_cman_config(model, **kw):
    errors = []
    if kw.get('expert_mode') is None:
        return (True, {})

    cman = model.getCMANPtr()
    expected_votes = kw.get('expected_votes')
    if expected_votes and not expected_votes.isspace():
        try:
            cman.setExpectedVotes(expected_votes)
        except:
            errors.append(_('Invalid value for expected votes: %s') % expected_votes)
    else:
        cman.delExpectedVotes()

    quorum_dev_poll = kw.get('quorum_dev_poll')
    if quorum_dev_poll and not quorum_dev_poll.isspace():
        try:
            cman.setQuorumDevPoll(quorum_dev_poll)
        except:
            errors.append(_('Invalid value for quorum device poll time: %s') % quorum_dev_poll)
    else:
        cman.delQuorumDevPoll()

    shutdown_timeout = kw.get('shutdown_timeout')
    if shutdown_timeout and not shutdown_timeout.isspace():
        try:
            cman.setShutdownTimeout(shutdown_timeout)
        except:
            errors.append(_('Invalid value for shutdown timeout: %s') % shutdown_timeout)
    else:
        cman.delShutdownTimeout()

    udp_port = kw.get('port')
    if udp_port and not udp_port.isspace():
        try:
            cman.setPort(udp_port)
        except:
            errors.append(_('Invalid value for CMAN UDP port: %s') % udp_port)
    else:
        cman.delPort()

    crypt_key = kw.get('keyfile')
    if crypt_key and not crypt_key.isspace():
        try:
            cman.setKeyFile(crypt_key)
        except:
            errors.append(_('Invalid value for encryption key path: %s') % crypt_key)
    else:
        cman.delKeyFile()

    cluster_id = kw.get('cluster_id')
    if cluster_id and not cluster_id.isspace():
        try:
            cman.setClusterId(cluster_id)
        except:
            errors.append(_('Invalid value for cluster ID: %s') % cluster_id)
    else:
        cman.delClusterId()

    ccsd_poll = kw.get('ccsd_poll')
    if ccsd_poll and not ccsd_poll.isspace():
        try:
            cman.setCcsdPoll(ccsd_poll)
        except:
            errors.append(_('Invalid value for ccsd poll interval: %s') % ccsd_poll)
    else:
        cman.delCcsdPoll()

    cman.setHashClusterId(kw.get('hash_cluster_id') is not None)
    cman.setUpgrading(kw.get('upgrading') is not None)
    cman.setDisallowed(kw.get('disallowed') is not None)
    cman.setDisableOpenAIS(kw.get('disable_openais') is not None)
    return (len(errors) < 1, {'errors': errors})

def validate_rm_config(model, **kw):
    errors = []
    if kw.get('expert_mode') is None:
        return (True, {})

    rm = model.getResourceManagerPtr()

    status_child_max = kw.get('status_child_max')
    if status_child_max and not status_child_max.isspace():
        try:
            rm.setStatusChildMax(status_child_max)
        except:
            errors.append(_('Invalid value for number of status threads: %s') % status_child_max)
    else:
        rm.delStatusChildMax()

    status_poll_interval = kw.get('status_poll_interval')
    if status_poll_interval and not status_poll_interval.isspace():
        try:
            rm.setStatusPollInterval(status_poll_interval)
        except:
            errors.append(_('Invalid value for status poll interval: %s') % status_poll_interval)
    else:
        rm.delStatusPollInterval()

    transition_throttling = kw.get('transition_throttling')
    if transition_throttling and not transition_throttling.isspace():
        try:
            rm.setTransitionThrottling(transition_throttling)
        except:
            errors.append(_('Invalid value for transition throttling: %s') % transition_throttling)
    else:
        rm.delTransitionThrottling()

    rm.setCentralProcessing(kw.get('central_processing') is not None)
    
    return (len(errors) < 1, {'errors': errors})

def validate_dlm_config(model, **kw):
    errors = []
    if kw.get('expert_mode') is None:
        return (True, {})

    dlm = model.getDLMPtr()

    protocol = kw.get('protocol')
    if protocol and not protocol.isspace():
        try:
            dlm.setProtocol(protocol)
        except:
            errors.append(_('Invalid value for lowcomms protocol: %s') % protocol)
    else:
        dlm.delProtocol()

    timewarn = kw.get('timewarn')
    if timewarn and not timewarn.isspace():
        try:
            dlm.setTimeWarn(timewarn)
        except:
            errors.append(_('Invalid value for number of centiseconds a lock can block %s:') % timewarn)
    else:
        dlm.delTimeWarn()

    drop_resources_time = kw.get('drop_resources_time')
    if drop_resources_time and not drop_resources_time.isspace():
        try:
            dlm.setDropResourcesTime(drop_resources_time)
        except:
            errors.append(_('Invalid value for drop resources time %s:') % drop_resources_time)
    else:
        dlm.delDropResourcesTime()

    drop_resources_count = kw.get('drop_resources_count')
    if drop_resources_count and not drop_resources_count.isspace():
        try:
            dlm.setDropResourcesCount(drop_resources_count)
        except:
            errors.append(_('Invalid value for drop resources count %s:') % drop_resources_count)
    else:
        dlm.delDropResourcesCount()

    drop_resources_age = kw.get('drop_resources_age')
    if drop_resources_age and not drop_resources_age.isspace():
        try:
            dlm.setDropResourcesAge(drop_resources_age)
        except:
            errors.append(_('Invalid value for drop resources age %s:') % drop_resources_age)
    else:
        dlm.delDropResourcesAge()

    dlm.setLogDebug(kw.get('log_debug') is not None)
    dlm.setEnableFencing(kw.get('enable_fencing') is not None)
    dlm.setEnableDeadlk(kw.get('enable_deadlk') is not None)
    dlm.setEnableQuorum(kw.get('enable_quorum') is not None)
    dlm.setEnablePlock(kw.get('enable_plock') is not None)
    dlm.setPlockOwnership(kw.get('plock_ownership') is not None)
    dlm.setPlockDebug(kw.get('plock_debug') is not None)
    dlm.setPlockRateLimit(kw.get('plock_rate_limit') is not None)
    
    return (len(errors) < 1, {'errors': errors})

def validate_gfscontrold_config(model, **kw):
    errors = []
    if kw.get('expert_mode') is None:
        return (True, {})

    gfscontrold = model.getGFSControldPtr()

    drop_resources_time = kw.get('drop_resources_time')
    if drop_resources_time and not drop_resources_time.isspace():
        try:
            gfscontrold.setDropResourcesTime(drop_resources_time)
        except:
            errors.append(_('Invalid value for drop resources time %s:') % drop_resources_time)
    else:
        gfscontrold.delDropResourcesTime()

    drop_resources_count = kw.get('drop_resources_count')
    if drop_resources_count and not drop_resources_count.isspace():
        try:
            gfscontrold.setDropResourcesCount(drop_resources_count)
        except:
            errors.append(_('Invalid value for drop resources count %s:') % drop_resources_count)
    else:
        gfscontrold.delDropResourcesCount()

    drop_resources_age = kw.get('drop_resources_age')
    if drop_resources_age and not drop_resources_age.isspace():
        try:
            gfscontrold.setDropResourcesAge(drop_resources_age)
        except:
            errors.append(_('Invalid value for drop resources age %s:') % drop_resources_age)
    else:
        gfscontrold.delDropResourcesAge()

    gfscontrold.setEnableWithdraw(kw.get('enable_withdraw') is not None)
    gfscontrold.setEnablePlock(kw.get('enable_plock') is not None)
    gfscontrold.setPlockOwnership(kw.get('plock_ownership') is not None)
    gfscontrold.setPlockDebug(kw.get('plock_debug') is not None)
    gfscontrold.setPlockRateLimit(kw.get('plock_rate_limit') is not None)
    return (len(errors) < 1, {'errors': errors})

def validate_groupd_config(model, **kw):
    errors = []
    if kw.get('expert_mode') is None:
        return (True, {})

    groupd = model.getGroupPtr()
    groupd.setCompat(kw.get('groupd_compat') is not None)
    return (len(errors) < 1, {'errors': errors})

def validate_clvmd_config(model, **kw):
    errors = []
    if kw.get('expert_mode') is None:
        return (True, {})

    clvmd = model.getClvmdPtr()
    interface = kw.get('interface')
    if interface and not interface.isspace():
        try:
            clvmd.setInterface(interface)
        except:
            errors.append(_('Invalid value for clvmd interface: %s') % interface)
    else:
        clvmd.delInterface()
    return (len(errors) < 1, {'errors': errors})

def validate_cluster_config_form(model, **kw):
    conf_page = kw.get('page')
    if not conf_page:
        return (False, {'errors': [ _('No config page was given') ] })

    if conf_page == 'Fence':
        return validate_fenced_config(model, **kw)
    elif conf_page == 'General':
        return validate_general_config(model, **kw)
    elif conf_page == 'Network':
        return validate_network_config(model, **kw)
    elif conf_page == 'RRP':
        return validate_rrp_config(model, **kw)
    elif conf_page == 'Logging':
        return validate_log_config(model, **kw)
    elif conf_page == 'QDisk':
        return validate_qdisk_config(model, **kw)
    elif conf_page == 'cman':
        return validate_cman_config(model, **kw)
    elif conf_page == 'rm':
        return validate_rm_config(model, **kw)
    elif conf_page == 'dlm':
        return validate_dlm_config(model, **kw)
    elif conf_page == 'gfs_controld':
        return validate_gfscontrold_config(model, **kw)
    elif conf_page == 'groupd':
        return validate_groupd_config(model, **kw)
    elif conf_page == 'clvmd':
        return validate_clvmd_config(model, **kw)

    return (False, {'errors':
            [ _('Unknown value %s for page was given') % conf_page ]})

def validate_node_fence_level(fence_level, model, node, xml_str):
    errors = []
    nodename = node.getName()
    try:
        if not xml_str:
            raise Exception, 'no fence XML'
        doc = minidom.parseString(xml_str)
    except:
        return (False, {'errors': [ _('Unable to parse fence XML data for fence level %d') % fence_level ]})

    levels = node.getFenceMethods()
    try:
        method_id = levels[min(1, fence_level - 1)].getAttribute('name')
        if not method_id:
            raise Exception, 'No method ID'
        fence_method = Method()
        fence_method.setName(method_id)
        levels[min(1, fence_level - 1)] = fence_method
    except Exception, e:
        fence_method = Method()
        fence_method.setName(fence_level)

    forms = doc.getElementsByTagName('form')
    if len(forms) < 1:
        delete_target = None
        for l in levels:
            # delete the fence level
            if l.getAttribute('name') == method_id:
                delete_target = l
                break
        if delete_target is not None:
            try:
                node.getFenceNode().removeChild(delete_target)
            except Exception, e:
                return (False, {'errors': ['An error occurred while deleting fence method %s' % method_id ]})
        else:
            return (True, {'messages': ['No changes were made'] })

    form_hash = {}
    for i in forms:
        form_id = i.getAttribute('id')
        if not form_id:
            continue
        ielems = i.getElementsByTagName('input')
        if not ielems or len(ielems) < 1:
            continue

        dummy_form = {}

        for i in ielems:
            try:
                input_type = str(i.getAttribute('type'))
            except Exception, e:
                continue

            if not input_type or input_type == 'button':
                continue

            try:
                dummy_form[str(i.getAttribute('name'))] = str(i.getAttribute('value'))
            except Exception, e:
                log.exception("ielem")

        if len(dummy_form) < 1:
            continue

        if dummy_form.has_key('fence_instance'):
            try:
                parent = dummy_form['parent_fencedev']
            except:
                return (False, {'errors': [ 'Unable to determine what device the current instance uses' ]})

            try:
                form_hash[parent][1].append(dummy_form)
                del dummy_form['fence_instance']
            except Exception, e:
                return (False, {'errors': [ 'Unable to determine what device the current instance uses' ]})
        else:
            form_hash[form_id] = (dummy_form, list())

    fh_keys = form_hash.keys()
    fh_keys.sort()
    for i in fh_keys:
        fencedev_name = None
        fencedev_unknown = False

        try:
            fence_form, instance_list = form_hash[i]
        except Exception, e:
            log.exception("fence list")

        try:
            fence_type = fence_form['fence_type']
            if not fence_type:
                raise Exception, 'fence type is blank'
        except Exception, e:
            fence_type = None
            log.exception("fence type")

        if fence_form.has_key('existing_device'):
            try:
                fencedev_name = fence_form['name']
                if not fencedev_name.strip():
                    raise Exception, 'no fence name'
            except Exception, e:
                errors.append(_('You must provide a unique name for all fence devices'))
                continue

            if fence_type is None:
                # An unknown fence device agent. Pull the data out of
                # the model and persist it and all instances.
                # All we care about is its name.
                fencedev_unknown = True
            else:
                if not fence_form.has_key('sharable'):
                    # If it's a shared fence device that already exists, the
                    # user could not have edited it so it's safe to pull the
                    # existing entry from the model. All we need is the
                    # device name, and nothing
                    # else needs to be done here.
                    #
                    # For an existing non-shared device update the device
                    # in the model, since the user could have edited it.
                    retcode, retmsg = validateFenceDevice(model, **fence_form)
                    if retcode != True:
                        errors.extend(retmsg)
                        continue
                    else:
                        fencedev_name = retmsg

                    # Add back the tags under the method block
                    # for the fence instance
                    if fence_type == 'fence_manual':
                        instance_list.append({'name': fencedev_name, 'nodename': nodename })
                    else:
                        instance_list.append({'name': fencedev_name })
        else:
            # The user created a new fence device.
            retcode, retmsg = validateNewFenceDevice(model, **fence_form)
            if retcode != True:
                errors.extend(retmsg)
                continue
            else:
                fencedev_name = retmsg

            # If it's not shared, we need to create an instance form
            # so the appropriate XML goes into the <method> block inside
            # <node><fence>. All we need for that is the device name.
            if not fence_form.has_key('sharable'):
                if fence_type == 'fence_manual':
                    instance_list.append({'name': fencedev_name, 'nodename': nodename })
                else:
                    instance_list.append({'name': fencedev_name })

        if fencedev_unknown is True:
            # Save any instances for this fence device.
            pass

        for inst in instance_list:
            retcode, retobj = validate_fenceinstance(fencedev_name, fence_type, **inst)
            if retcode != True:
                errors.extend(retobj)
                continue
            fence_method.addChild(retobj)

        fence_node = node.getFenceNode()
        found_target = False
        for idx in xrange(len(levels)):
            if levels[idx].getAttribute('name') == method_id:
                found_target = True
                break

        if found_target is False:
            # There's a fence block, but no relevant method
            # block
            fence_node.addChild(fence_method)

    return (len(errors) < 1, {'errors': errors})

def validate_node_fence_form(model, **kw):
    errors = []
    nodename = kw.get('node')
    if not nodename:
        return (False, {'errors': [ _('No node name was given') ]})

    try:
        node = model.retrieveNodeByName(nodename)
    except:
        return (False, {'errors': [ _('Unable to find node "%s" in the cluster configuration') % nodename ]})

    ret = validate_node_fence_level(1, model, node, kw.get('level1_xml'))
    if ret[0] is False:
        errors.extend(ret[1].get('errors'))
    ret = validate_node_fence_level(2, model, node, kw.get('level2_xml'))
    if ret[0] is False:
        errors.extend(ret[1].get('errors'))

    return (len(errors) < 1, {'errors': errors})

def validate_node_prop_settings_form(nodename, model, **kw):
    errors = []
    warnings = []

    node = model.retrieveNodeByName(nodename)
    if not node:
        errors.append(_('Unable to find node "%s" in the cluster.conf node list') % nodename)
        return (False, {'errors': errors })

    nodedbobj = get_node_by_name(nodename)
    if nodedbobj is None:
        # TODO node db obj has gone AWOL. We need to recreate this.
        errors.append(_('Unable to find node "%s" in the database') % nodename)
        return (False, {'errors': errors })

    votes = kw.get('votes')
    if votes:
        try:
            votes = int(votes)
            if votes < 1:
                raise ValueError
            node.setVotes(votes)
            if votes != 1:
                warnings.append(_('Setting node votes to a value greater than 1 for any node will disable Quorum Disk functionality'))
        except:
            errors.append(_('Invalid value given for votes: %s') % kw.get('votes'))

    ricci_host = kw.get('ricci_host')
    if ricci_host:
        nodedbobj.hostname = ricci_host

    ricci_port = kw.get('ricci_port')
    try:
        ricci_port = int(ricci_port)
        if ricci_port == 0 or ricci_port != ricci_port & 0xffff:
            raise ValueError
        nodedbobj.port = ricci_port
    except:
        errors.append(_('Invalid value for ricci TCP port: "%s"') % kw.get('ricci_port'))

    if kw.get('expert_mode'):
        dlm_lock_weight = kw.get('weight')
        if dlm_lock_weight and not dlm_lock_weight.isspace():
            try:
                node.setWeight(dlm_lock_weight)
            except:
                errors.append(_('Invalid DLM lock weight: %s') % dlm_lock_weight)
        else:
            node.delWeight()

    return (len(errors) == 0, {'errors': errors, 'warnings': warnings})

def validate_add_user(name, **kw):
    err = create_user_db_obj(name)
    if not err:
        return (True, {})
    return (False, {'errors': [err]})

def validate_user_perms(name, **kw):
    errors = []

    user = name
    if not user:
        errors.append(_('No user was specified'))
        return (False, {'errors': errors})

    try:
        user = User.by_user_name(user)
    except:
        log.exception('Looking up user object for %s' % user)
        user = None

    if not user:
        errors.append(_('Unknown user: %s') % user)
        return (False, {'errors': errors})

    new_group_list = []
    for k in kw:
        if k[:5] == 'role:':
            gname = k[5:]
            try:
                gobj = Group.by_group_name(gname)
            except:
                gobj = None
                log.exception('group %s' % gname)
            if not gobj:
                errors.append(_('Unknown permission: %s') % gname)
                continue
            new_group_list.append(gobj)
    user.groups = new_group_list
    DBSession.flush()
    DBSession.refresh(user)
    return (True, {})

def validate_luci_log_levels(**kw):
    errors = []

    log_root = kw.get('log_level_root')
    if log_root:
        log_root = log_root.upper()
        cur_logger = logging.getLogger('')
        try:
            cur_logger.setLevel(log_root)
        except ValueError:
            errors.append(_("Invalid log level for root: %s") % log_root)
        except:
            log.exception("Setting log level for root")
            errors.append(_("Unable to set log level for root to %s") % log_root)

    log_tg_i18n = kw.get('log_level_tg.i18n')
    if log_tg_i18n:
        log_tg_i18n = log_tg_i18n.upper()
        cur_logger = logging.getLogger('tg.i18n')
        try:
            cur_logger.setLevel(log_tg_i18n)
        except ValueError:
            errors.append(_("Invalid log level for tg.i18n: %s") % log_tg_i18n)
        except:
            log.exception("Setting log level for tg.i18n")
            errors.append(_("Unable to set log level for tg.i18n to %s") % log_tg_i18n)

    log_sqlalchemy = kw.get('log_level_sqlalchemy')
    if log_sqlalchemy:
        log_sqlalchemy = log_sqlalchemy.upper()
        cur_logger = logging.getLogger('sqlalchemy')
        try:
            cur_logger.setLevel(log_sqlalchemy)
            try:
                # Change child and related loggers to match
                log_manager = cur_logger.manager
                for i in log_manager.loggerDict.keys():
                    if i[:11] == "sqlalchemy." or i in ('txn'):
                        cur_logger = logging.getLogger(i)
                        cur_logger.setLevel(log_sqlalchemy)
            except:
                log.exception("Updating child loggers for sqlalchemy")
        except ValueError:
            errors.append(_("Invalid log level for sqlalchemy: %s") % log_sqlalchemy)
        except:
            log.exception("Setting log level for sqlalchemy")
            errors.append(_("Unable to set log level for sqlalchemy to %s") % log_sqlalchemy)

    log_luci = kw.get('log_level_luci')
    if log_luci:
        log_luci = log_luci.upper()
        cur_logger = logging.getLogger('luci')
        try:
            cur_logger.setLevel(log_luci)
            try:
                # Change child loggers to match
                log_manager = cur_logger.manager
                for i in log_manager.loggerDict.keys():
                    if i[:5] == "luci.":
                        cur_logger = logging.getLogger(i)
                        cur_logger.setLevel(log_sqlalchemy)
            except:
                log.exception("Updating child loggers for sqlalchemy")
        except ValueError:
            errors.append(_("Invalid log level for luci: %s") % log_luci)
        except:
            log.exception("Setting log level for luci")
            errors.append(_("Unable to set log level for luci to %s") % log_tg_i18n)

    if len(errors) > 0:
        return (False, {'errors': errors})
    return (True, {})
