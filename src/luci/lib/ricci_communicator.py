# Copyright (C) 2006-2011 Red Hat, Inc.
#
# This program is free software; you can redistribute
# it and/or modify it under the terms of version 2 of the
# GNU General Public License as published by the
# Free Software Foundation.

from xml.dom import minidom, Node
from ricci_defines import LUCI_LOG_DEBUG_NETWORK, DEFAULT_RICCI_PORT, RICCI_CONNECT_FAILURES_MAX
import socket
import struct
import ssl

from tg import config
from luci.lib.helpers import ugettext as _

import logging
log = logging.getLogger(__name__)

class RicciError(Exception):
    def __init__(self, args):
        super(RicciError, self).__init__(args)
        try:
            self.ss.settimeout(None)
        except:
            pass

class RicciCommunicator:
    def __init__(self, hostname, port=DEFAULT_RICCI_PORT):
        self.__hostname = hostname
        self.__port = int(port)
        self.ss = None
        self.__cluname = None
        self.__clualias = None
        self.__reported_hostname = None
        self.__os = None
        self.__dom0 = None

        self.__timeout_init = 3
        self.__timeout_auth = 4
        self.__timeout_short = 6
        self.__timeout_long = 600

        self.__cluster_version = (-1, 'unknown', None)

        # Which file to use as certificate for communicating to ricci
        # has to be specified in the configuration
        try:
            self.__cert_pem = config['ricci.cert_pem']
        except KeyError, e:
            errmsg = _('Missing ricci.cert_pem value in the configuration')
            log.exception(errmsg)
            raise RicciError, errmsg

        try:
            s = None
            for res in socket.getaddrinfo(self.__hostname, self.__port,
                            socket.AF_UNSPEC, socket.SOCK_STREAM):
                af, socktype, proto, canonname, sa = res
                try:
                    s = socket.socket(af, socktype, proto)
                    break
                except socket.error, msg:
                    s = None
                    continue

            if s is None:
                raise RicciError, 'socket() failed'

            try:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,
                    struct.pack('ii', 1, 0))
            except:
                log.exception('setting SO_LINGER')

            self.ss = ssl.wrap_socket(s,
                        certfile=self.__cert_pem,
                        cert_reqs=ssl.CERT_NONE)
        except Exception, e:
            try:
                if self.ss:
                    self.ss.close()
                    self.ss = None
                elif s:
                    s.close()
            except:
                pass

            errmsg = 'Unable to establish an SSL connection to %s:%d' \
                        % (self.__hostname, self.__port)
            if len(e.args) > 1:
                # Case for ssl.SSLError and socket.error that has 'args'
                # formed by (errno, string) pair.
                errmsg = '%s: %s' % (errmsg, e.args[1])
            log.exception(errmsg)
            raise RicciError, errmsg

        connection_failures = 0
        while True:
            try:
                self.ss.settimeout(self.__timeout_init)
                self.ss.connect((self.__hostname, self.__port))
            except Exception, e:
                connection_failures += 1
                if connection_failures >= RICCI_CONNECT_FAILURES_MAX:
                    errmsg = 'Unable to establish an SSL connection to %s:%d after %d tries. Is the ricci service running?' \
                                % (self.__hostname, self.__port, RICCI_CONNECT_FAILURES_MAX)
                    if len(e.args) > 1:
                        errmsg = '%s: %s' % (errmsg, e.args[1])
                    log.exception(errmsg)
                    raise RicciError, errmsg
                else:
                    log.exception('Connect to %s:%d failed: %s (will retry %d more times)'
                        % (self.__hostname, self.__port, str(e),
                           RICCI_CONNECT_FAILURES_MAX - connection_failures))
            else:
                break
                
        # receive ricci header
        try:
            hello = self.__receive(self.__timeout_init)
            if LUCI_LOG_DEBUG_NETWORK is True:
                log.debug('Recv header from %s:%d "%s"'
                    % (self.__hostname, self.__port, hello.toxml()))

            self.__authed = hello.firstChild.getAttribute('authenticated') == 'true'
            self.__cluname = hello.firstChild.getAttribute('clustername')
            self.__clualias = hello.firstChild.getAttribute('clusteralias')
            self.__reported_hostname = hello.firstChild.getAttribute('hostname')
            self.__os = hello.firstChild.getAttribute('os')
            self.__dom0 = hello.firstChild.getAttribute('xen_host') == 'true'
            self.__cluster_version = resolve_cluster_version(self.__os)
        except:
            err_msg = 'Error receiving header from %s:%d' % (self.__hostname, self.__port)
            log.exception('%s' % err_msg)
            raise RicciError, err_msg

    def __del__(self):
        if self.ss is not None:
            try:
                self.ss.close()
            except:
                pass

    def cluster_version(self):
        return self.__cluster_version

    def hostname(self):
        if LUCI_LOG_DEBUG_NETWORK is True:
            log.debug('hostname: [auth=%d] hostname = %s [%d]'
                % (self.__authed, self.__hostname, self.__port))
        return self.__hostname

    def authed(self):
        if LUCI_LOG_DEBUG_NETWORK is True:
            log.debug('authed: reported authed = %d for %s:%d'
                % (self.__authed, self.__hostname, self.__port))
        return self.__authed

    def system_name(self):
        if LUCI_LOG_DEBUG_NETWORK is True:
            log.debug('system_name: [auth=%d] name = %s for %s:%d'
                % (self.__authed, self.__reported_hostname,
                   self.__hostname, self.__port))
        return self.__reported_hostname

    def cluster_info(self):
        if LUCI_LOG_DEBUG_NETWORK is True:
            log.debug('info [auth=%d] (%s,%s) for %s:%d'
                % (self.__authed, self.__cluname, self.__clualias,
                   self.__hostname, self.__port))
        return (self.__cluname, self.__clualias)

    def os(self):
        if LUCI_LOG_DEBUG_NETWORK is True:
            log.debug('os [auth=%d] reported os = %s for %s:%d' \
                % (self.__authed, self.__os, self.__hostname, self.__port))
        return self.__os

    def dom0(self):
        if LUCI_LOG_DEBUG_NETWORK is True:
            log.debug('dom0 [auth=%d] dom0 = %s for %s:%d' \
                % (self.__authed, self.__dom0, self.__hostname, self.__port))
        return self.__dom0

    def fingerprint(self):
        fp = self.ss.peer_fingerprint()
        if LUCI_LOG_DEBUG_NETWORK is True:
            log.debug('fp [auth=%d] fp for %s:%d = %s' \
                % (self.__authed, self.__hostname, self.__port, fp))
        return fp

    def auth(self, password):
        if self.authed():
            return True

        # send request
        doc = minidom.Document()
        ricci = doc.createElement('ricci')
        ricci.setAttribute('version', '1.0')
        ricci.setAttribute('function', 'authenticate')
        ricci.setAttribute('password', password)
        doc.appendChild(ricci)
        self.__send(doc, self.__timeout_auth)

        # receive response
        resp = self.__receive(self.__timeout_auth)
        self.__authed = resp.firstChild.getAttribute('authenticated') == 'true'

        if LUCI_LOG_DEBUG_NETWORK is True:
            log.debug('auth call to %s:%d returned %d' \
                % (self.__hostname, self.__port, self.__authed))

        if self.__authed:
            try:
                self.__cluname = resp.firstChild.getAttribute('clustername')
                self.__clualias = resp.firstChild.getAttribute('clusteralias')
                self.__reported_hostname = resp.firstChild.getAttribute('hostname')
                self.__os = resp.firstChild.getAttribute('os')
                self.__dom0 = resp.firstChild.getAttribute('xen_host') == 'true'
            except Exception, e:
                log.exception('Error authenticating to %s:%d'
                    % (self.__hostname, self.__port))
        else:
            log.info('Authentication to the ricci agent at %s:%d failed'
                % (self.__hostname, self.__port))

        return self.__authed

    def unauth(self):
        doc = minidom.Document()
        ricci = doc.createElement('ricci')
        ricci.setAttribute('version', '1.0')
        ricci.setAttribute('function', 'unauthenticate')
        doc.appendChild(ricci)
        self.__send(doc, self.__timeout_auth)
        resp = self.__receive(self.__timeout_auth)

        try:
            ret = resp.firstChild.getAttribute('success')
            if LUCI_LOG_DEBUG_NETWORK is True:
                log.debug('unauthenticate %s for %s:%d'
                    % (ret, self.__hostname, self.__port))

            if ret != '0':
                raise Exception, 'invalid response: %s' % ret
        except Exception, e:
            errstr = _('Error unauthenticating to the ricci agent at %s:%d: %s') \
                        % (self.__hostname, self.__port, e.args[0])
            log.exception(errstr)
            raise RicciError, errstr
        return True

    def process_batch(self, batch_xml, async=False):
        if LUCI_LOG_DEBUG_NETWORK is True:
            log.debug('process_batch("%s"): [auth=%d async=%d] to %s:%d'
                % (batch_xml.toxml(),
                   self.__authed, async, self.__hostname, self.__port))

        if not self.__authed:
            raise RicciError, _('Not authenticated to the ricci agent at %s:%d') % (self.__hostname, self.__port)

        # construct request
        doc = minidom.Document()
        ricci = doc.createElement('ricci')
        ricci.setAttribute('version', '1.0')
        ricci.setAttribute('function', 'process_batch')

        async_str = None
        if async:
            async_str = 'true'
        else:
            async_str = 'false'
        ricci.setAttribute('async', async_str)

        doc.appendChild(ricci)
        ricci.appendChild(batch_xml)

        # send request
        try:
            self.__send(doc, self.__timeout_short)
        except Exception, e:
            errstr = _('Error sending XML batch command to %s:%d: %s') \
                        % (self.__hostname, self.__port, e.message)
            if LUCI_LOG_DEBUG_NETWORK is True:
                log.exception("%s | XML: %s" % (errstr, doc.toxml()))
            log.error(errstr)
            raise RicciError, errstr

        # receive response
        doc = self.__receive(self.__timeout_long)
        if LUCI_LOG_DEBUG_NETWORK is True:
            log.debug('Received XML from %s:%d: "%s"'
                % (self.__hostname, self.__port, doc.toxml()))

        if doc.firstChild.getAttribute('success') != '0':
            log.info('Batch command to %s:%d failed'
                % (self.__hostname, self.__port))
            raise RicciError, _('The last ricci command sent to %s:%d failed') \
                    % (self.__hostname, self.__port)

        batch_node = None
        for node in doc.firstChild.childNodes:
            if node.nodeType == Node.ELEMENT_NODE:
                if node.nodeName == 'batch':
                    batch_node = node

        if batch_node is None:
            errmsg = _('Missing <batch/> tag in ricci response from %s:%d') \
                        % (self.__hostname, self.__port)
            log.error(errmsg)
            if LUCI_LOG_DEBUG_NETWORK is True:
                log.debug("%s | XML: %s" % (errmsg, doc.toxml()))
            raise RicciError, errmsg

        return batch_node

    def batch_run(self, batch_str, async=True):
        if not self.__authed:
            raise RicciError, _('Not authenticated to the ricci agent at %s:%d') \
                    % (self.__hostname, self.__port)
        try:
            batch_xml_str = '<?xml version="1.0" ?><batch>%s</batch>' \
                                % batch_str
            if LUCI_LOG_DEBUG_NETWORK is True:
                log.debug('run batch "%s" for %s:%d'
                    % (batch_xml_str, self.__hostname, self.__port))
            batch_xml = minidom.parseString(batch_xml_str).firstChild
        except Exception, e:
            errmsg = _('Batch XML reply from %s:%d is malformed') \
                        % (self.__hostname, self.__port)
            log.exception("%s | XML: %s" % (errmsg, batch_xml_str))
            raise RicciError, errmsg

        try:
            ricci_xml = self.process_batch(batch_xml, async)
            if LUCI_LOG_DEBUG_NETWORK is True:
                log.debug('batch_run[%d]: Received "%s" from %s:%d'
                    % (async, ricci_xml.toxml(), self.__hostname, self.__port))
        except Exception, e:
            log.exception('batch_run[%d] error for "%s" at %s:%d'
                % (async, batch_xml_str, self.__hostname, self.__port))
            return None

        doc = minidom.Document()
        doc.appendChild(ricci_xml)
        return doc

    def batch_status(self, batch_id):
        ret = {
            'host': self.__hostname,
            'port': self.__port,
            'batchid': batch_id,
            'ricci_msg': '',
            'ricci_code': '',
            'db_status': '',
            'status': '',
            'module_total': '',
            'module_offset': '',
        }

        try:
            batch = self.batch_report(batch_id)
            if batch is None:
                # Either it's done or we asked for the wrong thing.
                log.error('%s:%d: unknown batchid %s' % (self.__hostname, self.__port, str(batch_id)))
                ret['status'] = _('batch id does not exist')
                return (0, ret, 0)
            (module_offset, module_total) = batch_status(batch)
            module_offset = max(1, module_offset)
            ret['module_total'] = module_total
            ret['module_offset'] = module_offset
        except Exception, e:
            log.exception('batch status: %s:%d'
                % (self.__hostname, self.__port))
            ret['status'] = _('error retrieving batch report: %s') % str(e)
            return (-2, ret, 0)

        try:
            code, ricci_msg = extract_module_status(batch, module_offset)
            ret['ricci_code'] = code
            if ricci_msg:
                ret['ricci_msg'] = ricci_msg
        except Exception, e:
            ret['status'] = _('error retrieving batch status: %s') % str(e)
            return (-2, ret, 0)

        ret_code = 1
        if code == -101:
            # Running now
            ret['status'] = _('module execution in progress')
        elif code == -102:
            # Waiting to run
            ret['status'] = _('module execution scheduled')
        elif code == -103:
            # Removed from batch execution
            ret['status'] = _('module removed from execution schedule')
            ret_code = 0
        elif code == -104:
            # Failed to run
            ret['status'] = _('module failed to execute')
            ret_code = -1
        elif code == -2:
            # Completed with API error
            ret['status'] = _('API error')
            ret_code = -1
        elif code == -1:
            # Completed with undefined error
            ret['status'] = _('unexpected error occurred')
            ret_code = -1
        elif code == 0:
            # Completed with no error
            ret['status'] = _('completed sucessfully')
            ret_code = 0
        elif code > 0:
            # Completed with defined error
            ret['status'] = _('error occurred')
            ret_code = -1
        else:
            # Unexpected code received from ricci
            log.error('Batch %s on %s:%d unknown code %d'
                % (str(batch_id), self.__hostname, self.__port, code))
            ret['status'] = _('unexpected error code %d encountered') % code
            ret_code = -2
        return (ret_code, ret, module_total - module_offset)

    def batch_report(self, batch_id):
        if not self.__authed:
            raise RicciError,  _('Not authenticated to the ricci agent at %s:%d') \
                    % (self.__hostname, self.__port)

        # construct request
        doc = minidom.Document()
        ricci = doc.createElement('ricci')
        ricci.setAttribute('version', '1.0')
        ricci.setAttribute('function', 'batch_report')
        ricci.setAttribute('batch_id', str(batch_id))
        doc.appendChild(ricci)

        # send request
        self.__send(doc, self.__timeout_short)

        # receive response
        doc = self.__receive(self.__timeout_short)

        if doc.firstChild.getAttribute('success') == '12':
            return None
        if doc.firstChild.getAttribute('success') != '0':
            raise RicciError, _('Error retrieving batch %s report from %s:%d') \
                % (str(batch_id), self.__hostname, self.__port)

        batch_node = None
        for node in doc.firstChild.childNodes:
            if node.nodeType == Node.ELEMENT_NODE:
                if node.nodeName == 'batch':
                    batch_node = node
        if batch_node is None:
            raise RicciError, _('Missing <batch/> in ricci response from %s:%d') \
                % (self.__hostname, self.__port)
        return batch_node

    def __send(self, xml_doc, timeout):
        try:
            self.ss.settimeout(timeout)
            self.ss.write(xml_doc.toxml())
        except ssl.SSLError, e:
            # Only ssl.SSLError expected which is formed by (errno, string) pair.
            errstr = _('Error sending batch command to %s:%d: %s') \
                % (self.__hostname, self.__port, e.args[1])

            if LUCI_LOG_DEBUG_NETWORK is True:
                log.debug("%s | XML: %s" % (errstr, xml_doc.toxml()))
            log.exception(errstr)
            raise RicciError, errstr

        if LUCI_LOG_DEBUG_NETWORK is True:
            log.debug('Sent XML "%s" to %s:%d'
                % (xml_doc.toxml(), self.__hostname, self.__port))

        try:
            self.ss.settimeout(None)
        except:
            pass
        return

    def __receive(self, timeout):
        self.ss.settimeout(timeout)
        xml_in = []
        doc = None
        err = 0

        while doc is None:
            try:
                cur_chunk = self.ss.read()
                if LUCI_LOG_DEBUG_NETWORK is True:
                    log.debug('recv XML "%s" from %s:%d' \
                        % (cur_chunk, self.__hostname, self.__port))
                if len(cur_chunk) == 0:
                    break
                xml_in.append(cur_chunk)
            except ssl.SSLError, e:
                # Only ssl.SSLError expected which is formed by (errno, string) pair.
                errstr = _('Error reading from %s:%d: %s') \
                            % (self.__hostname, self.__port, e)
                log.exception(errstr)
                err += 1
                if err >= 5:
                    raise RicciError, errstr

            doc = None
            try:
                doc = minidom.parseString(''.join(xml_in))
            except Exception, e:
                doc = None
                continue

        if not doc or not doc.firstChild:
            errmsg = _('An empty XML response was received from %s:%d') \
                        % (self.__hostname, self.__port)
            log.error(errmsg)
            raise RicciError, errmsg

        cur_nodename = None
        try:
            cur_nodename = doc.firstChild.nodeName
            if cur_nodename != 'ricci':
                raise Exception, _('Expected first XML child node to be "<ricci>"')
        except Exception, e:
            if cur_nodename == 'Timeout_reached_without_valid_XML_request':
                errmsg = _('Connection to %s:%d timed out') \
                            % (self.__hostname, self.__port)
            else:
                errmsg = _('Invalid ricci XML response from %s:%d') \
                            % (self.__hostname, self.__port)

            if LUCI_LOG_DEBUG_NETWORK is True:
                log.exception("%s | XML: %s" % (errmsg, ''.join(xml_in)))
            else:
                log.exception(errmsg)
            raise RicciError, errmsg

        try:
            self.ss.settimeout(None)
        except:
            pass
        return doc

def ricci_get_called_hostname(self, ricci):
    return ricci.hostname()
def ricci_get_reported_hostname(self, ricci):
    return ricci.system_name()
def ricci_get_os(self, ricci):
    return ricci.os()
def ricci_get_dom0(self, ricci):
    return ricci.dom0()
def ricci_get_cluster_info(self, ricci):
    return ricci.cluster_info()
def ricci_get_authenticated(self, ricci):
    return ricci.authed()
def ricci_authenticate(self, ricci, password):
    return ricci.auth(password)
def ricci_unauthenticate(self, ricci):
    return ricci.unauth()

########## helpers to process batch as returned by ricci #############

# check the status of batch
# returns (int num, int total)
# * total:
#        total number of modules in batch
# * num:
#        if num == total:
#            all modules in the batch completed successfuly
#        if num > 0:
#            last seq. number of module that successfuly finished
#        if num < 0:
#            module (-num) failed (next module won't be processed)

def batch_status(batch_xml):
    if batch_xml.nodeName != 'batch':
        errmsg = _('Invalid ricci reply. Expecting <batch> got <%s>') \
                    % batch_xml.nodeName
        if LUCI_LOG_DEBUG_NETWORK:
            log.debug('%s | XML: %s' % (errmsg, batch_xml.toxml()))
        raise RicciError, errmsg

    total = 0
    last = 0
    for node in batch_xml.childNodes:
        if node.nodeType == Node.ELEMENT_NODE:
            if node.nodeName == 'module':
                total = total + 1
                status = node.getAttribute('status')
                if status == '0':
                    # success
                    last = last + 1
                elif status == '3' or status == '4':
                    # failure
                    last = last + 1
                    last = last - 2 * last

    if LUCI_LOG_DEBUG_NETWORK is True:
        log.debug('batch status("%s") -> (%d, %d)'
            % (batch_xml.toxml(), last, total))
    return (last, total)

# extract error_code from module's response
# * module_num:
#            1-based seq. number of module to process
#
# returns (int error_code, string error_msg)
# * error_code: each module defines own error codes, which are >0
#        -101 - in progress
#        -102 - scheduled
#        -103 - removed from schedule
#        -104 - failed to execute module
#
#        >-3 - module executed. Following codes are defined:
#         -2 - API error
#         -1 - undefined error occured (msg not necesarily very informative)
#          0 - no error (msg is empty string)
#         >0 - predefined error has occured
#                (check respective API, msg will be fully descriptive)
# * error_msg: error message

def extract_module_status(batch_xml, module_num=1):
    if batch_xml.nodeName != 'batch':
        errmsg = _('Invalid ricci reply. Expecting <batch> got %s') \
                    % batch_xml.nodeName

        if LUCI_LOG_DEBUG_NETWORK is True:
            log.debug("%s | XML: %s" % (errmsg, batch_xml.toxml()))
        raise RicciError, errmsg

    c = 0
    for node in batch_xml.childNodes:
        if node.nodeType == Node.ELEMENT_NODE:
            if node.nodeName == 'module':
                module_xml = node
                c = c + 1
                if c == module_num:
                    status = module_xml.getAttribute('status')
                    if status == '0' or status == '4':
                        # module executed, dig deeper into request
                        for node_i in module_xml.childNodes:
                            if node_i.nodeType == Node.ELEMENT_NODE:
                                if node_i.nodeName == 'API_error':
                                    return -2, 'API error'
                                elif node_i.nodeName == 'response':
                                    for node_j in node_i.childNodes:
                                        if node_j.nodeType == Node.ELEMENT_NODE:
                                            if node_j.nodeName == 'function_response':
                                                code = -11111111
                                                msg = 'BUG'
                                                for var in node_j.childNodes:
                                                    if var.nodeType == Node.ELEMENT_NODE:
                                                        if var.nodeName == 'var':
                                                            if var.getAttribute('name') == 'success' and var.getAttribute('value') == 'true':
                                                                return 0, ''
                                                            elif var.getAttribute('name') == 'error_code':
                                                                code = int(var.getAttribute('value'))
                                                            elif var.getAttribute('name') == 'error_description':
                                                                msg = var.getAttribute('value')
                                                return code, msg

                    elif status == '1':
                        return -102, 'module scheduled for execution'
                    elif status == '2':
                        return -101, 'module is being executed'
                    elif status == '3':
                        return -104, 'failed to locate/execute module'
                    elif status == '5':
                        return -103, 'module removed from schedule'

    errmsg = _('no module %d in the ricci XML reply') % module_num

    if LUCI_LOG_DEBUG_NETWORK is True:
        log.debug("%s | XML: %s" % (errmsg, batch_xml.toxml()))
    raise RicciError, errmsg

def resolve_cluster_version(uname_str):
    if 'Santiago' in uname_str:
        return (3, 'RHEL', uname_str[uname_str.find('6.'):].split(' ')[0])
    elif 'Tikanga' in uname_str:
        return (2, 'RHEL', uname_str[uname_str.find('5.'):].split(' ')[0])
    elif 'Nahant' in uname_str:
        return (1, 'RHEL', uname_str[uname_str.find('4.'):].split(' ')[0])
    elif 'Lovelock' in uname_str:
        return (3, 'Fedora', '15')
    elif 'Laughlin' in uname_str:
        return (3, 'Fedora', '14')
    elif 'Goddard' in uname_str:
        return (3, 'Fedora', '13')
    elif 'Constantine' in uname_str:
        return (3, 'Fedora', '12')
    elif 'Leonidas' in uname_str:
        return (3, 'Fedora', '11')
    elif 'Cambridge' in uname_str:
        return (3, 'Fedora', '10')
    elif 'Sulphur' in uname_str:
        return (3, 'Fedora', '9')
    elif 'Werewolf' in uname_str:
        return (2, 'Fedora', '8')
    elif 'Moonshine' in uname_str:
        return (2, 'Fedora', '7')
    elif 'Zod' in uname_str:
        return (2, 'Fedora', '6')
    elif 'Bordeaux' in uname_str:
        return (2, 'Fedora', '5')
    elif 'Stentz' in uname_str:
        return (1, 'Fedora', '4')
    return (-1, 'unknown', None)
