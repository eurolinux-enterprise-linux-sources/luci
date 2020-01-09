%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
%{!?python_version: %global python_version %(%{__python} -c "import sys; print sys.version[:3]")}

# Default root directory for luci state files
%global def_lucistatedir    %{_sharedstatedir}/%{name}
%global def_lucilogdir      %{_localstatedir}/log/%{name}
# Default luci-specific user/group (using the same values)
%global def_luciusername    %{name}
# Default port running luci binds at
%global def_luciport        8084

# Conditional assignment allowing external redefinition during build stage
%{!?lucistatedir:   %global lucistatedir  %{def_lucistatedir}}
%{!?lucilogdir:     %global lucilogdir    %{def_lucilogdir}}
%{!?luciusername:   %global luciusername  %{def_luciusername}}
%{!?lucigroupname:  %global lucigroupname %{luciusername}}
%{!?luciport:       %global luciport      %{def_luciport}}


# Denotes the service name of installed luci (affects initscript name etc.)
%global luciservice         %{name}

%global lucicertdir         %{lucistatedir}/certs
%global luciconfdir         %{lucistatedir}/etc
%global lucidatadir         %{lucistatedir}/data
# Where runtime data (e.g. PID file, sessions, cache) are stored
%global luciruntimedatadir  %{_localstatedir}/run/%{luciservice}

# Configuration derived from values above
%global lucibaseconfig      %{luciconfdir}/luci.ini
%global lucicertconfig      %{luciconfdir}/cacert.config
%global lucicertpem         %{lucicertdir}/host.pem
%global lucidbfile          %{lucidatadir}/%{name}.db

%global lucicachedir        %{luciruntimedatadir}/cache
%global lucisessionsdir     %{luciruntimedatadir}/sessions
%global lucilogfile         %{lucilogdir}/%{luciservice}.log
%global lucilockfile        %{_localstatedir}/lock/subsys/%{luciservice}
%global lucipidfile         %{luciruntimedatadir}/%{luciservice}.pid

%global luciinitscript      %{_initddir}/%{luciservice}
%global lucisysconfig       %{_sysconfdir}/sysconfig/%{luciservice}
# This should reflect the Spec file for python-paste-script
%global lucilauncher        /usr/bin/python -Es %{_bindir}/paster
%global lucilogrotateconfig %{_sysconfdir}/logrotate.d/%{luciservice}
%global lucipamconfig       %{_sysconfdir}/pam.d/%{luciservice}
%global lucisasl2config     %{_sysconfdir}/sasl2/%{luciservice}.conf

## keep around for git snapshots
## global alphatag 0.b9faf868074git

Name:           luci
Version:        0.26.0
Release:        1%{?alphatag:.%{alphatag}}%{?dist}

Summary:        Web-based high availability administration application
URL:            https://fedorahosted.org/cluster/wiki/Luci
License:        GPLv2
Group:          Applications/System

Source0:        http://people.redhat.com/rmccabe/luci/luci-%{version}.tar.bz2
# Avoid ez_setup downloading setuptools if missing (already in BuildRequires)
#Patch0:         %{name}-setup.patch

%if 0%{?rhel}
ExclusiveArch:  i686 x86_64
%endif

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  python-devel python-setuptools
BuildRequires:  cyrus-sasl-devel
# Used to create paster_plugins.txt in egg-info dir (setup.py: setup_requires)
BuildRequires:  python-paste-script

Requires:       TurboGears2 python-repoze-who-friendlyform
Requires:       python-paste >= 1.7.2-5
# Initscript requirements (iproute: ``ip'' tool, used to get IP addresses)
Requires:       coreutils iproute sed
# Not necessarily needed, we only drop a file to /etc/logrotate.d/
#Requires:       logrotate
# Required for "start" action in initscript (one-off certificate generation)
Requires:       openssl
# Authentication service against which luci users are authenticated;
# this version is required as it initially searches config files in /etc/sasl2
# (see http://www.postfix.org/SASL_README.html#server_cyrus_location)
Requires:       cyrus-sasl >= 2.1.22
# Following package is required to ensure PAM authentication via saslauthd
# works out-of-the-box (saslauthd from cyrus-sasl uses "pam" mechanism
# by default, but does not require it; also needed for /etc/pam.d directory)
Requires:       pam

# glibc-common:getent; shadow-utils:groupadd,useradd; util-linux-ng:/sbin/nologin
Requires(pre):    glibc-common shadow-utils util-linux-ng
Requires(post):   chkconfig
Requires(preun):  chkconfig initscripts
Requires(postun): initscripts


%description
Luci is a web-based high availability administration application built on the
TurboGears 2 framework.


%prep
%setup -q
#%patch0 -b .setup
# Important parameters for luci and start of its service
%{__python} setup.py saveopts --filename=setup.cfg pkg_prepare  \
                     --username="%{luciusername}"               \
                     --groupname="%{lucigroupname}"             \
                     --port="%{luciport}"
# State directory for luci + nested dirs and files
%{__python} setup.py saveopts --filename=setup.cfg pkg_prepare  \
                     --statedir="%{lucistatedir}"               \
                     --baseconfig="%{lucibaseconfig}"           \
                     --certconfig="%{lucicertconfig}"           \
                     --certpem="%{lucicertpem}"                 \
                     --dbfile="%{lucidbfile}"
# Work files spread in the system directories
%{__python} setup.py saveopts --filename=setup.cfg pkg_prepare  \
                     --runtimedatadir="%{luciruntimedatadir}"   \
                     --cachedir="%{lucicachedir}"               \
                     --sessionsdir="%{lucisessionsdir}"         \
                     --pidfile="%{lucipidfile}"                 \
                     --lockfile="%{lucilockfile}"               \
                     --logfile="%{lucilogfile}"
# System files (initscript and configuration files)
%{__python} setup.py saveopts --filename=setup.cfg pkg_prepare  \
                     --initscript="%{luciinitscript}"           \
                     --sysconfig="%{lucisysconfig}"             \
                     --launcher="%{lucilauncher}"           \
                     --logrotateconfig="%{lucilogrotateconfig}" \
                     --pamconfig="%{lucipamconfig}"             \
                     --sasl2config="%{lucisasl2config}"


%build
%{__python} setup.py build


%install
%{__rm} -rf "%{buildroot}"

# Luci Python package (incl. extensions)
# Note: '--root' implies setuptools involves distutils to do old-style install
%{__python} setup.py install --skip-build --root "%{buildroot}"

# State directory for luci (directory structure + ghosted files)
%{__install} -d "%{buildroot}%{lucistatedir}"
%{__install} -d "%{buildroot}%{luciconfdir}"
touch "%{buildroot}%{lucibaseconfig}"
%{__install} -d "%{buildroot}%{lucicertdir}"
touch "%{buildroot}%{lucicertpem}"
%{__install} -d "%{buildroot}%{lucidatadir}"
touch "%{buildroot}%{lucidbfile}"

# Work files spread in the system (directories)
%{__install} -d "%{buildroot}%{luciruntimedatadir}"
%{__install} -d "%{buildroot}%{lucilogdir}"


%clean
%{__rm} -rf "%{buildroot}"


%files
%defattr(-,%{luciusername},%{lucigroupname},-)

%attr(-,root,root) %doc README COPYING

%attr(-,root,root) %{python_sitearch}/%{name}/
%attr(-,root,root) %{python_sitearch}/%{name}-%{version}-py%{python_version}.egg-info/

# State directory for luci + nested files/dirs
#
# Most of files stated here is created ad-hoc but are added here as "ghosts"
# so they are associated with the package and their permissions can be
# verified using "rpm -V luci"
# Note: those "ghosted" files that should be definitely removed upon package
#       removal should not be marked with "config" and viceversa
%{lucistatedir}/
%config(noreplace)           %{lucicertconfig}
# Base configuration contains sensitive records and should be totally
# restricted from unauthorized access (created ad-hoc during 1st run)
%attr(0640,-,-)       %ghost %{lucibaseconfig}
# Database file has to persist (also may contain sensitive records)
%attr(0640,-,-)       %ghost %{lucidbfile}
# ... and so the generated certificate (due to problem with as-yet missing
# reauthentication dialog so changing this certificate during upgrade would
# mean a need for removing clusters and re-adding them back)
%attr(0600,-,-)       %ghost %{lucicertpem}

# Work files spread in the system directories
%ghost                       %{luciruntimedatadir}/
%{lucilogdir}/
# Log file can contain sensitive records and should be totally restricted from
# unauthorized access (same permissions presumably used for auto-rotated logs)
%attr(0640,-,-)       %ghost %{lucilogfile}

# System files (initscript and configuration files)
%attr(0755,root,root)                    %{luciinitscript}
%attr(-,root,root)    %config(noreplace) %{lucisysconfig}
%attr(-,root,root)    %config(noreplace) %{lucilogrotateconfig}
%attr(-,root,root)    %config(noreplace) %{lucipamconfig}
%attr(-,root,root)    %config(noreplace) %{lucisasl2config}


%pre
getent group %{lucigroupname} >/dev/null || groupadd -r %{lucigroupname}
getent passwd %{luciusername} >/dev/null || \
    useradd -r -g %{lucigroupname} -d %{lucistatedir} -s /sbin/nologin \
    -c "%{name} high availability management application" %{luciusername}

if [ "$1" -eq "2" ]; then
# If we're upgrading from luci 0.22.x, we need to move
# the old config out of the way, as this file is no longer
# marked %config, but %ghost in luci 0.23.0 and later
    conf_first_word="$((head -1 %{lucibaseconfig} 2>/dev/null || echo 'empty')|awk '{print $2}')"
    if [ "$conf_first_word" = "luci" ]; then
        mv -f %{lucibaseconfig} %{lucibaseconfig}.rpmsave
    fi
fi
exit 0

%post
/sbin/chkconfig --add "%{luciservice}" || :

%preun
if [ "$1" == "0" ]; then
    /sbin/service "%{luciservice}" stop &>/dev/null
    /sbin/chkconfig --del "%{luciservice}"
fi
exit 0

%postun
if [ "$1" -ge "1" ]; then
    /sbin/service "%{luciservice}" condrestart &>/dev/null || :
fi


%changelog
* Mon Jan 23 2012 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-1
- New upstream release 0.26.0

* Mon Aug 01 2011 Ryan McCabe <rmccabe@redhat.com> - 0.25.0-1
- New upstream release 0.25.0

* Fri Apr 15 2011 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.24.0-2
- Fix spec file from 0.24.0 import:
  - readd alphatag to support git snapshots
  - drop exclusivearch on fedora
  - readd missing changelog entries

* Thu Apr 14 2011 Ryan McCabe <rmccabe@redhat.com> - 0.24.0-1
- New upstream release (0.24.0)

- Fix bz472972 (Separate the Oracle 10g Failover Instance in Conga to two resources called "Oracle Instance" and "Oracle Listener")
- Fix bz536841 (Need ability to change number of votes for a node through luci)
- Fix bz557234 (luci update to handle private network/hostnames for cluster create/config)
- Fix bz600057 (Fix node uptime display)
- Fix bz600078 (Warn about qdisk use for certain configurations)
- Fix bz605932 (Missing "reset to defaults" button in qdisk configuration)
- Fix bz613155 (running luci init script as non-root user results in traceback)
- Fix bz613871 (luci should not give ungraceful error messages when encountering fence devices that it does not recognize/support)
- Fix bz614963 (Python 2.6 deprecation of BaseException.message)
- Fix bz616239 (Need option to completely destroy cluster)
- Fix bz617586 (Implement progress dialog for long-running operations)
- Fix bz617587 (Luci doesn't display underlying errors)
- Fix bz618701 (Spaces in cluster name confuse luci)
- Fix bz620343 (Consider renaming "Services" to "Service Groups")
- Fix bz620373 (Consider changing the tab order)
- Fix bz620377 (Drop-down menus do not remember the selection)
- Fix bz622562 (Need to add support for unfencing conf. generation for SAN fencing agents and fence_scsi)
- Fix bz624558 (replace broadcast option with udpu)
- Fix bz624716 (luci displays misleading error status on initial cluster configuration pages)
- Fix bz632344 (Enable centralized logging configuration via Luci)
- Fix bz633983 (Luci does not handle parameter "nodename" related to fence_scsi fence agent correctly)
- Fix bz636267 ("Update" buttons at "Fence Devices" tab do effectively nothing)
- Fix bz636300 (Egenera fence agent: specifying username not arranged correctly)
- Fix bz637223 (Cisco UCS Fencing Agent)
- Fix bz639107 (Add luci support for configuring fence_rhev)
- Fix bz639111 (Support configuration of non-critical resources)
- Fix bz639120 (Create "expert" user mode)
- Fix bz639123 (Disable action buttons when no nodes are selected)
- Fix bz639124 (Reconcile local database with changes in cluster membership made outside of luci)
- Fix bz643488 (inconsistent er/upper casing)
- Fix bz659014 (Luci returns an Error 500 when accessing node configuration with FQDN names)
- Fix bz666971 (Disable updates to static routes by RHCS IP tooling)
- Fix bz678366 (fence management not fully functional)
- Fix bz678424 (can't add node to existing cluster)
- Fix bz682843 (luci still tries to setup obsolete smb.sh Resource)

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.22.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Dec 13 2010 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.22.6-2
- Fix bad merge from upstream spec file

* Mon Dec 13 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.6-1
- New upstream release (0.22.6)

* Tue Nov 16 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.5-1
- New upstream release (0.22.5)
- Display all fence and resource agents for Fedora clusters
- Add support for fence_rhevm and fence_cisco_ucs
- Cleanup of cluster.conf handler
- Fixes for running on TG2.1
- Allow configuration of saslauthd
- Enforce a 15 minute idle session timeout
- Add back node uptime to the cluster node list display
- Allow users to configure the ricci address and port for cluster nodes
- Fixes to cope with cluster membership changes made outside of luci

* Thu Oct 21 2010 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.22.4-2.0.b9faf868074git
- Fix CVE-2010-3852 (bug #645404)

* Thu Aug 19 2010 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.22.4-1.0.b9faf868074git
- New upstream release (0.22.4)
- Steal fixes from upstream git up to b9faf868074git
  Fix bz622562 (add support for unfencing)
  Fix bz624819 (add compatibility with TG2.1)
- Update spec file to support alphatag

* Sun Aug 08 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.4-1
- Version 0.22.4
- Remove extra debugging logging from the fix for bz619220
- Fix bz614130 (implement tomcat6 resource agent)
- Fix bz618578 (ip resource should have netmask field)
- Fix bz615926 (luci does not handle qdisk / cman config correctly)
- Fix bz619220 (Luci does extra queries which slows down page load)
- Fix bz619652 (luci sometimes prints a traceback when deleting multiple nodes at the same time)
- Fix bz619641 (luci init script prints a python traceback when status is queried by a non-root user)

* Fri Jul 30 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.3-1
- Version 0.22.3

* Thu Jul 29 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-11
- Fix bz614433 (cannot configure ipport for fence agents)
- Fix bz617575 (Unclear options when configuring a cluster)
- Fix bz617591 (Some fields when adding an IP address are unclear)
- Fix bz617602 (Fields in "Fence Daemon Properties" have no units)
- Fix bz618577 (wrong message displayed when adding ip resource)
- Fix bz619220 (Luci does extra queries which slows down page load)

* Tue Jul 26 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-10
- Additional fixes for bz600027 (Fix cluster service creation/configuration UX issues)
- Additional fixes for bz600055 ("cluster busy" dialog does not work)
- Fix bz618424 (Can't remove nodes in node add dialog or create cluster dialog)
- Fix bz616382 (luci db error removing a node from a cluster)
- Fix bz613871 (luci should not give ungraceful error messages when encountering fence devices that it does not recognize/support)

* Mon Jul 26 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-9
- Fix bz600027 (Fix cluster service creation/configuration UX issues)
- Fix bz600040 (Add nodes to existing cluster does not work)
- Fix bz600045 (Removing nodes from existing clusters fails)
- Fix bz600055 ("cluster busy" dialog does not work)
- Fix bz613868 (Remove fence_virsh from luci UI since this fence is not supported with RHEL HA/Cluster)
- Fix bz614434 (adding an IP resource ends with an error 500)
- Fix bz614439 (adding GFS2 resource type in RHEL6 cluster is "interesting")
- Fix bz615096 (Traceback when unchecking "Prioritized" in Failover Domains)
- Fix bz615468 (When creating a new failover domain, adding nodes has no effect)
- Fix bz615872 (unicode error deleting a cluster)
- Fix bz615889 (luci cannot start an imported cluster)
- Fix bz615911 (luci shows many unsupported fence devices when adding a new fence device)
- Fix bz615917 (adding per node fence instance results in error 500 if no fence devices are configured)
- Fix bz615929 (luci generated cluster.conf with fence_scsi fails to validate)
- Fix bz616094 (Deleting a fence device which is in use, causes a traceback on Nodes page)
- Fix bz616228 (Clicking on cluster from manage clusters page results in traceback (500 error))
- Fix bz616230 (Clicking on the join button doesn't work on nodes page)
- Fix bz616244 (Clicking on the leave button doesn't work on nodes page.)

* Wed Jul 14 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-8
- Fix bz600021 (Fix node fence configuration UX issues)

* Tue Jul 13 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-7
- Build fix for bz600056

* Tue Jul 13 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-6
- Build fix for bz600056

* Tue Jul 13 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-5
- Fix bz604740 (Support nfsserver resource agent which is for NFSv4 and NFSv3)
- Fix bz600056 (Replace logo image)

* Fri Jul 09 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-4
- Fix bz600059 (Hide optional fields for fence_scsi)
- Fix bz600077 (cman "two_node" attribute should not be set when using qdisk)
- Fix bz600083 (Add text to broadcast mode to note that it is for demos only - no production support)
- Fix bz605780 (Qdisk shouldn't be part of the main page, it should be in the configuration tab)

* Fri Jun 18 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-3
- Fix bz598859 (Adding fence_xvm fence device through luci interface throws TypeError Traceback)
- Fix bz599074 ("Use same password for all nodes" doesn't work.)
- Fix bz599080 (Conga ignores "reboot nodes" check box)
- Fix bz600047 (luci allows deletion of global resources that are used by services)
- Fix bz600050 (luci requires wrongly requires users to fill interval / tko / minimum score / votes fields for qdisk configuration)
- Fix bz600052 (luci allows deletion of the last qdisk heuristics row)
- Fix bz600058 (ssh_identity field values are dropped)
- Fix bz600060 (Formatting error on fence devices overview page)
- Fix bz600061 (Default values not populated in advanced network configuration)
- Fix bz600066 (Update resource agent labels)
- Fix bz600069 (Configuration page always returns to General Properties Page)
- Fix bz600071 (If luci cannot communicate with the nodes they don't appear in the list of nodes)
- Fix bz600073 (Update resource agent list)
- Fix bz600074 (Fix display error on the resource list page)
- Fix bz600075 (update fence_virt / fence_xvm configuration)
- Fix bz600076 (When creating a cluster no default radio button is selected for Download Packages/Use locally installed packages)
- Fix bz600079 (Unable to edit existing resources)
- Fix bz600080 (Homebase page only shows a '-' for Nodes Joined)
- Fix bz602482 (Multicast settings are not relayed to cluster.conf and no default)
- Fix bz603833 ("Nodes Joined" in main page is inaccurate when no nodes have joined)

* Tue Jun 01 2010 Chris Feist <cfeist@redhat.com> - 0.22.2-2
- Fix missing requires which will cause some installations to fail
- Resolves: rhbz#598725

* Fri May 26 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-1
- Fix for bugs related to cluster service creation and editing (bz593836).

* Wed May 26 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.1-3
- Fix remaining unresolved issues for 593836
  - Make sure the cluster version is updated when creating services
  - Fix a bug that caused IP resources to fail in services

* Wed May 26 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.1-2
- Rebuild to fix a bug introduced during last build.

* Wed May 26 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.1-1
- Fix service creation, display, and edit.
- Fix qdisk heuristic submission.

* Wed May 19 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.0-16
- Rebase to upstream

* Mon May 17 2010 Chris Feist <cfeist@redhat.com> - 0.22.0-13
- Added static UID/GID for luci user
- Resolves: rhbz#585988

* Wed May 12 2010 Chris Feist <cfeist@redhat.com> - 0.22.0-11
- Add support for PAM authentication
- Resync with main branch
- Resolves: rhbz#518206

* Wed May 12 2010 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.21.0-8
- Do not build on ppc and ppc64.
  Resolves: rhbz#590987

* Tue Apr 27 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.0-4
- Update from devel tree.

* Thu Apr 22 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.0-3
- Update from development tree.

* Thu Apr 08 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.0-2
- Update from development tree.

* Tue Mar 09 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.0-1
- Rebase to luci version 0.22.0

* Mon Mar  1 2010 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.21.0-7
- Resolves: rhbz#568005
- Add ExcludeArch to drop s390 and s390x

* Tue Jan 19 2010 Ryan McCabe <rmccabe@redhat.com> - 0.21.0-6
- Remove dependency on python-tg-devtools

* Wed Nov 04 2009 Ryan McCabe <rmccabe@redhat.com> - 0.21.0-4
- And again.

* Wed Nov 04 2009 Ryan McCabe <rmccabe@redhat.com> - 0.21.0-2
- Fix missing build dep.

* Tue Nov 03 2009 Ryan McCabe <rmccabe@redhat.com> - 0.21.0-1
- Add init script.
- Run as the luci user, not root.
- Turn off debugging.

* Fri Sep 25 2009 Ryan McCabe <rmccabe@redhat.com> - 0.20.0-1
- Initial build.
