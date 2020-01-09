%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
%{!?python_version: %global python_version %(%{__python} -c "import sys; print sys.version[:3]")}

# Default root directory for luci state files
%global def_lucistatedir    %{_sharedstatedir}/%{name}
%global def_lucilogdir      %{_localstatedir}/log/%{name}
# Default luci-specific user/group (using the same values)
%global def_luciusername    %{name}
%global def_luciuid         141
%global def_lucigid         141
# Default port running luci binds at
%global def_luciport        8084

# Conditional assignment allowing external redefinition during build stage
%{!?lucistatedir:   %global lucistatedir  %{def_lucistatedir}}
%{!?lucilogdir:     %global lucilogdir    %{def_lucilogdir}}
%{!?luciusername:   %global luciusername  %{def_luciusername}}
%{!?lucigroupname:  %global lucigroupname %{luciusername}}
%{!?luciport:       %global luciport      %{def_luciport}}
%{!?luciuid:        %global luciuid       %{def_luciuid}}
%{!?lucigid:        %global lucigid       %{def_lucigid}}

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
%global lucilauncher        %{_bindir}/paster
%global luciproxylauncher   %{_sbindir}/%{luciservice}
%global lucilogrotateconfig %{_sysconfdir}/logrotate.d/%{luciservice}
%global lucipamconfig       %{_sysconfdir}/pam.d/%{luciservice}
%global lucisasl2config     %{_sysconfdir}/sasl2/%{luciservice}.conf


Name:           luci
Version:        0.26.0
Release:        78%{?dist}

Summary:        Web-based high availability administration application
URL:            https://fedorahosted.org/cluster/wiki/Luci
# The entire source code is GPLv2 except luci/lib/pyopenssl_wrapper.py (MIT)
License:        GPLv2 and MIT
Group:          Applications/System

Source0:        http://people.redhat.com/rmccabe/luci/luci-%{version}.tar.bz2
Source1:        sort-images-0.2.tar.gz

# this denotes builds in which luci.ini file should be generated anew
%global breakpoints_luci_ini \
                0.23.0-1     \
                0.26.0-53    \
                0.26.0-72

Patch0: bz671285.patch
Patch1: bz786584.patch
Patch2: bz690621.patch
Patch3: bz749668-2.patch
Patch4: bz796731.patch
Patch5: bz786584-2.patch
Patch6: bz800239.patch
Patch7: bz690621-2.patch
Patch8: bz803398.patch
Patch9: bz801491.patch
Patch10: bz740835.patch
Patch11: bz772314.patch
Patch12: bz820402.patch
Patch13: bz758821.patch
Patch14: bz820402-2.patch
Patch15: bz758821-2.patch
Patch16: bz853151.patch
Patch17: bz826951.patch
Patch18: bz740867-add_support_for_the_ibm_ipdu_fence_device.patch
# after a discussion, centering of the popup-messages was called off
#Patch19: bz773491-center_popup_messages.patch
Patch20: bz807344-fix_handling_of_resource_and_services.patch
Patch21: bz807344-2-fixes_for_resource_service_failover_naming.patch
Patch22: bz815666-fix_unfence_display_on_node_page.patch
Patch23: bz821928-add_support_for_fence_ipmilan_privlvl.patch
Patch24: bz822502-add_support_for_nfsrestart.patch
Patch25: bz856253-fix_double_click_on_add_existing_dialog.patch
Patch26: bz809892-add_the_ability_to_remove_users.patch
Patch27: bz815666-add_back_missing_unfence_patch.patch
Patch28: bz865300-add_support_for_fence_eaton_snmp.patch
Patch29: bz865533-add_support_for_fence_hpblade.patch
Patch30: bz865533-fix_label_on_fence_hpblade_form.patch
Patch31: bz860042-allow_global_resources_to_be_referenced_multiple_times.patch
Patch32: bz807344-3-fix-nonexistent-entities-handling.patch
Patch33: bz822502-add_missing_js_include.patch
Patch34: bz822502-fix_the_interaction_of_the_force_unmount_and.patch
Patch35: bz877188-error_out_if_max_restarts_is_set_but_not.patch
Patch36: bz877188-2-fix_handling_of_subtree_options.patch
Patch37: bz877392-fix_value_for_lvm_self_fence.patch
Patch38: bz881796-trailing_commas_that_cause_problems_for_some_old.patch
Patch39: bz881955-audit_of_resource_agent_checkbox_input.patch
Patch40: bz815666-fix_matching_of_unfence_blocks.patch
Patch41: bz877098.patch
Patch42: bz882995-update_unfence_when_renaming_fence_devices.patch
Patch43: bz877098-2.patch
Patch44: bz886678.patch
Patch45: bz880363-fix_garbled_error_messages.patch
Patch46: bz878960-don_t_let_anonymous_users_access_the_preferences_page.patch
Patch47: bz878149-fix_uncaught_exception.patch
Patch48: bz883008-add_support_for_fence_device_attributes.patch
Patch49: bz878149-2-fix_for_tracebacks_when_no_nodes_can_be_contacted.patch
Patch50: bz773491-make_pop_up_messages_act_like_static_status_messages.patch
Patch51: bz773491-make_pop_up_messages_act_like_static_status.patch
Patch52: bz883008-add_support_for_fence_scsi_delay_attribute.patch
Patch53: bz886517-enable_the_ricci_and_modclusterd_services_when_creating_a.patch
Patch54: bz886576-remove_useless_remove_this_instance_button.patch
Patch55: bz917747-add_support_for_missing_fence_devices.patch
Patch56: bz917814-ask_for_confirmation_when_removing_a_cluster.patch
Patch57: bz983693-update_oracle_agent_configuration.patch
Patch58: bz983693-add_support_for_tns_admin_in_oracle_agents.patch
Patch59: bz896244-1-default-syslog-facility-is-local4.patch
Patch60: bz896244-2-reduce-space-waste-by-loopifying-invariants.patch
Patch61: bz978479-fix-cluster_version-mismatch-upon-adding-2-nodes.patch
# needs more work
#Patch62: bz877999.patch
Patch63: bz1001835.patch
Patch64: bz1001836.patch
Patch65: bz1005385-1.patch
Patch66: bz1005385-2.patch
Patch67: bz883008-do_not_propagate_unfencing_to_conf.patch
Patch68: enforce-valid-code.patch
Patch69: bz723925-add_option_to_completely_disable_rgmanager.patch
Patch70: bz919243-don_t_allow_nfsclient_without_nfsexport.patch
Patch71: bz1070760-add_support_for_newly_added_nfsserver_statdport.patch
Patch72: bz1009309-add_named_to_the_resource_list.patch
Patch73: bz917771-add_support_for_configuring_missing_totem.patch
Patch74: bz1003062-don_t_write_type_attribute_for_oracledb_for.patch
Patch75: bz1004922-fix_default_value_for_post_join_delay.patch
Patch76: bz1008510-update_name_for_fence_egenera.patch
Patch77: bz1019853-support_configuring_self_fence_attribute_for.patch
Patch78: bz1061786-add_support_for_the_apache_httpd_attribute.patch
Patch79: bz1100817-fix_crash_when_config_contains_a_globally_defined.patch
Patch80: bz918795-add_support_for_fence_kdump.patch
Patch81: bz919225-add_support_for_sorting_by_columns_of_the.patch
Patch82: bz1004011-allow_configuration_of_more_fence_xvm_attributes.patch
Patch83: bz988446-fix_broken_display_on_permissions_page.patch
Patch84: bz855112-disallow_xml_unsafe_characters_in_attribute.patch
Patch85: bz917780-2.patch
Patch86: bz1004011-don_t_remove_attributes_from_xvm_fence_devs_in.patch
Patch87: bz991575.patch
Patch88: bz982771.patch
Patch89: bz917738-add_support_for_the_ip_prefer_interface_attr.patch
Patch90: bz1117398-add_support_for_the_bind_mount_resource.patch
Patch91: bz1117398-2-update_fence_brocade.patch
Patch92: bz1117398-3-add_support_for_the_reboot_on_pid_exhaustion.patch
Patch93: bz1117398-4-remove_mention_of_fenced_skip_undefined.patch
Patch94: bz1117398-5-add_support_for_the_postgres_8_startup_wait_attr.patch
Patch95: bz1117398-6-add_the_ssh_options_attribute_to_applicable_fence.patch
Patch96: bz1117398-7-add_support_for_the_no_kill_attribute_of_the_vm.patch
Patch97: bz1117398-8-add_support_for_the_use_findmnt_attribute.patch
Patch98: bz918795-update_the_fence_kdump_config_forms.patch
Patch99: bz919225-move_sort_arrows_for_resources.patch
Patch100: bz1100817-cope_better_with_editing_services_containing_vm.patch
Patch101: bz999324.patch
Patch102: bz1026374.patch
Patch103: bz1127286.patch
Patch104: bz855112-allow_in_xml_attribute_values.patch
Patch105: bz919225-fix_positioning_of_sort_arrows.patch
Patch106: bz919243-allow_nfsclient_to_be_a_child_of_nfsserver.patch
Patch107: bz1117398-remove_bad_default_values_for_startup_wait_and.patch
Patch108: bz1117398-2-remove_ssh_options_fields_from_fence_agents_that_do.patch
Patch109: bz1117398-3-support_newly_added_bind_mount_name_attribute.patch
Patch110: bz1100817-fix_editing_services_that_vm_references.patch
Patch111: bz1117398-fix_error_in_fence_lpar_form.patch
Patch112: bz1117398-2-fix_issues_with_bind_mount_resource_name_display.patch
Patch113: bz1100817-luci_fix_editing_services_that_vm_references.patch
Patch114: bz1136456-don_t_active_new_conf_if_any_of_the_nodes_didn_t.patch
Patch115: bz886526-add_a_cancel_button_to_the_services_add_resource.patch
Patch116: bz917761-add_support_for_miss_count_const.patch
Patch117: bz917773-add_support_for_rrp_problem_count_threshold.patch
Patch118: bz917781-indicate_that_shutdown_wait_is_ignored_for.patch
Patch119: bz1010400-add_support_for_the_fence_apc_cmd_prompt_attr.patch
Patch120: bz1100831-don_t_let_the_add_resource_button_disappear_after.patch
Patch121: bz919223-add_expand_and_collapse_buttons_for_services.patch
Patch122: bz1111249-add_a_stop_service_action_in_expert_mode.patch
Patch123: bz1112297-don_t_lose_nfsserver_nfspath_when_not_in_expert.patch
Patch124: bz919223-add_expand_collapse_buttons_for_each_inline.patch
Patch125: bz1112297-preserve_expert_mode_resource_attributes.patch
Patch126: bz1136456-warn_when_config_can_t_be_set_or_activated.patch
Patch127: bz1204910-update_fence_virt_fence_xvm_labels.patch
Patch128: bz1210683-add_support_for_fence_emerson_and_fence_mpath.patch
Patch129: bz1270958.patch
Patch130: bz1156167.patch
Patch131: bz1156187.patch
Patch132: use-stronger-hash-for-default-cert.patch
Patch133: bz1208649-luci_remove_references_to_named_sdb.patch
Patch134: bz988945-luci_fix_defaults_for_dlm_gfs_controld_plock_ownership.patch
Patch135: bz1285840-fix_allowed_values_for_totem_@secauth.patch
Patch136: bz1255207-support_alternate_timeout_attributes_for_fence_devices.patch
Patch137: bz1273954-allow_rrp_configuration_for_udpu.patch
Patch138: bz1285840-fix_handling_of_binary_totem_secauth_attribute.patch

ExclusiveArch:  i686 x86_64
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

# shadow-utils:groupadd,useradd; util-linux-ng:/sbin/nologin
Requires(pre):    shadow-utils util-linux-ng
Requires(post):   chkconfig
Requires(preun):  chkconfig initscripts
Requires(postun): initscripts


%description
Luci is a web-based high availability administration application built on the
TurboGears 2 framework.


%prep
%setup -q

%setup -q -T -D -a 1
pushd luci/public/images
cp -f ../../../sort-images/asc.gif .
cp -f ../../../sort-images/desc.gif .
cp -f ../../../sort-images/bg.gif .
cp -f ../../../sort-images/stop-temp-blue.png .
popd

%patch0 -p1 -b .bz671285
%patch1 -p1 -b .bz786584
%patch2 -p1 -b .bz690621
%patch3 -p1 -b .bz749668
%patch4 -p1 -b .bz796731
%patch5 -p1 -b .bz786584-2
%patch6 -p1 -b .bz800239
%patch7 -p1 -b .bz690621-2
%patch8 -p1 -b .bz803398
%patch9 -p1 -b .bz801491
%patch10 -p1 -b .bz740835
%patch11 -p1 -b .bz772314
%patch12 -p1 -b .bz820402
%patch13 -p1 -b .bz758821
%patch14 -p1 -b .bz820402-2
%patch15 -p1 -b .bz758821-2
%patch16 -p1 -b .bz853151
%patch17 -p1 -b .bz826951
%patch18 -p1 -b .bz740867.1
# explanation above
#patch19 -p1 -b .bz773491.1
%patch20 -p1 -b .bz807344.1
%patch21 -p1 -b .bz807344.2
%patch22 -p1 -b .bz815666.1
%patch23 -p1 -b .bz821928.1
%patch24 -p1 -b .bz822502.1
%patch25 -p1 -b .bz856253.1
%patch26 -p1 -b .bz809892.1
%patch27 -p1 -b .bz815666.1
%patch28 -p1 -b .bz865300.1
%patch29 -p1 -b .bz865533.1
%patch30 -p1 -b .bz865533.1
%patch31 -p1 -b .bz860042.1
%patch32 -p1 -b .bz807344-3
%patch33 -p1 -b .bz822502.1
%patch34 -p1 -b .bz822502.1
%patch35 -p1 -b .bz877188.1
%patch36 -p1 -b .bz877188.2
%patch37 -p1 -b .bz877392.1
%patch38 -p1 -b .bz881796.1
%patch39 -p1 -b .bz881955.1
%patch40 -p1 -b .bz815666.1
%patch41 -p1 -b .bz877098.1
%patch42 -p1 -b .bz882995.1
%patch43 -p1 -b .bz877098.2
%patch44 -p1 -b .bz886678
%patch45 -p1 -b .bz880363.1
%patch46 -p1 -b .bz878960.1
%patch47 -p1 -b .bz878149.1
%patch48 -p1 -b .bz883008.1
%patch49 -p1 -b .bz878149.2
%patch50 -p1 -b .bz773491.1
%patch51 -p1 -b .bz773491.2
%patch52 -p1 -b .bz883008.2
%patch53 -p1 -b .bz886517.1
%patch54 -p1 -b .bz886576.1
%patch55 -p1 -b .bz917747.1
%patch56 -p1 -b .bz917814.1
%patch57 -p1 -b .bz983693.1
%patch58 -p1 -b .bz983693.1
%patch59 -p1 -b .bz896244.1
%patch60 -p1 -b .bz896244.2
%patch61 -p1 -b .bz978479
# see above
#patch62 -p1 -b .bz877999
%patch63 -p1 -b .bz1001835
%patch64 -p1 -b .bz1001836
%patch65 -p1 -b .bz1005385-1
%patch66 -p1 -b .bz1005385-2
%patch67 -p1 -b .bz883008.3
%patch68 -p1 -b .prevent-invalid-code

%patch69 -p1 -b .bz723925.1
%patch70 -p1 -b .bz919243.1
%patch71 -p1 -b .bz1070760.1
%patch72 -p1 -b .bz1009309.1
%patch73 -p1 -b .bz917771.1
%patch74 -p1 -b .bz1003062.1
%patch75 -p1 -b .bz1004922.1
%patch76 -p1 -b .bz1008510.1
%patch77 -p1 -b .bz1019853.1
%patch78 -p1 -b .bz1061786.1
%patch79 -p1 -b .bz1100817.1
%patch80 -p1 -b .bz918795.1
%patch81 -p1 -b .bz919225.1
%patch82 -p1 -b .bz1004011.1
%patch83 -p1 -b .bz988446.1
%patch84 -p1 -b .bz855112.1
%patch85 -p1 -b .bz917780.2
%patch86 -p1 -b .bz1004011.1
%patch87 -p2 -b .bz991575
%patch88 -p2 -b .bz982771
%patch89 -p1 -b .bz917738.1
%patch90 -p1 -b .bz1117398.1
%patch91 -p1 -b .bz1117398.2
%patch92 -p1 -b .bz1117398.3
%patch93 -p1 -b .bz1117398.4
%patch94 -p1 -b .bz1117398.5
%patch95 -p1 -b .bz1117398.6
%patch96 -p1 -b .bz1117398.7
%patch97 -p1 -b .bz1117398.8
%patch98 -p1 -b .bz918795.2
%patch99 -p1 -b .bz919225.2
%patch100 -p1 -b .bz1100817.2
%patch101 -p1 -b .bz999324
%patch102 -p1 -b .bz1026374
%patch103 -p1 -b .bz1127286
%patch104 -p1 -b .bz855112.1
%patch105 -p1 -b .bz919225.1
%patch106 -p1 -b .bz919243.1
%patch107 -p1 -b .bz1117398.1
%patch108 -p1 -b .bz1117398.2
%patch109 -p1 -b .bz1117398.3
%patch110 -p1 -b .bz1100817.3
%patch111 -p1 -b .bz1117398.1
%patch112 -p1 -b .bz1117398.2
%patch113 -p1 -b .bz1100817.4
%patch114 -p1 -b .bz1136456.1
%patch117 -p1 -b .bz917773.1
%patch116 -p1 -b .bz917761.1
%patch118 -p1 -b .bz917781.1
%patch119 -p1 -b .bz1010400.1
%patch115 -p1 -b .bz886526.1
%patch120 -p1 -b .bz1100831.1
%patch121 -p1 -b .bz919223.1
%patch122 -p1 -b .bz1111249.1
%patch123 -p1 -b .bz1112297.1
%patch124 -p1 -b .bz919223.2
%patch125 -p1 -b .bz1112297.2
%patch126 -p1 -b .bz1136456.2
%patch127 -p1 -b .bz1204910.1
%patch128 -p1 -b .bz1210683.1
%patch129 -p1 -b .bz1270958
%patch130 -p1 -b .bz1156167
%patch131 -p1 -b .bz1156187
%patch132 -p1 -b .bz1156167.hash
%patch133 -p1 -b .bz1208649.1
%patch134 -p1 -b .bz988945.1
%patch135 -p1 -b .bz1285840.1
%patch136 -p1 -b .bz1255207.1
%patch137 -p1 -b .bz1273954.1
%patch138 -p1 -b .bz1285840.1

# Make sure no dependency is downloaded by modifying stock setup.cfg
# (this apparently cannot by used by calling saveopts subcommand
# as it would make sure it has setup_requires dependencies first)
# for local prep phase in case of not having python-paste-script
# installed, use something like this in $HOME/.pydistutils.cfg:
#     [easy_install]
#     find_links = /opt/or/any/other/path/for/easy_install
# then perform:
#     $ pushd /opt/or/any/other/path/for/easy_install
#     $ PYTHONPATH=${PYTHON_PATH:="$(pwd):$PYTHON_PATH"} easy_install \
#       --install-dir $(pwd) PasteScript
#     $ popd
sed -i.orig \
  '/\[easy_install\]/{s|\(.*\)|\1\nallow_hosts = None|;:1;n;/\[.*\]/d;s|^\([^#].*\)|\#\1|;t1}' \
  setup.cfg

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
                     --launcher="%{lucilauncher}"               \
                     --proxylauncher="%{luciproxylauncher}"     \
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
%config                      %{lucicertconfig}
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
%attr(0755,root,root)                    %{luciproxylauncher}
%attr(-,root,root)    %config(noreplace) %{lucisysconfig}
%attr(-,root,root)    %config(noreplace) %{lucilogrotateconfig}
%attr(-,root,root)    %config(noreplace) %{lucipamconfig}
%attr(-,root,root)    %config(noreplace) %{lucisasl2config}


# If we're upgrading from luci 0.22.x, we need to move the old config
# out of the way, as this file is no longer marked "config", but "ghost"
# in luci 0.23.0 and later; ditto when intended luci.ini content changes
# in a backward-incompatible way -> explicitly listed "breakpoints_luci_ini"
# ("pre" usage).
# Symmetrically, when we are transitioning down to unenlightened version
# (distinguished by rpm query to find out if this version is present)
# we need -- with the exception of "down to 0.22.x" (easily recoverable
# anyway) -- to move the old config as well ("preun" usage).
#
# NOTE inline backslashes doubled, newlines backslashed + no whitespaces around
%global breakpoints_luci_ini_fire \
    installed="$(rpm -q --queryformat="%%{V}-%%{R}\\n" --last -- %{name} \\\
                | sed -ne '/^[[:digit:]]/{s|\\(\\S*\\)\\s\\+$|\\1|;p}')"\
    new="%{version}-%{release}"  # NOTE "new"/"old" used loosely until settled\
    old=$(echo "${installed}" | sed -ne "/^${new}$/n;p"); old=${old:-"${new}"}\
    echo "${installed}" | grep -q "^${new}$"; taken_over=$?  # 0~true\
    old="${old%%.[a-z]*}"; new="${new%%.[a-z]*}"  # drop dist tags\
    [ ${taken_over} -eq 0 ] && orig="${new}" || orig="${old}"  # backup f. tail\
    # settle down old is not newer of the two and viceversa\
    if [ "$(echo -e "${old}\\n${new}" | sort -V | head -n1)" != "${old}" ]; then\
        temp="${new}"; new="${old}"; old="${temp}"\
    fi\
    # dummy (non-bisection) + optimistic (don't trigger on same-ver reinstall)\
    breakpoints="%{breakpoints_luci_ini}"  # neutralize newlines\
    for breakpoint in ${breakpoints}; do\
        [ "${breakpoint}" = "${old}" ] && continue\
        check_order=$(echo -en "${old}\\n${breakpoint}\\n${new}")\
        if [ "$(echo -e "${check_order}" | sort -V)" = "${check_order}" ]; then\
            mv -f --backup=t -- "%{lucibaseconfig}"{,".rpmsave-${orig}"} || :\
            break\
        fi\
    done


%pre
if [ "$1" -eq "2" ] && [ -f "%{lucibaseconfig}" ]; then
%{breakpoints_luci_ini_fire}
fi
/usr/sbin/groupadd -g %{lucigid} %{lucigroupname} 2> /dev/null
/usr/sbin/useradd -u %{luciuid} -g %{lucigid} -d /var/lib/luci -s /sbin/nologin -r \
    -c "%{name} high availability management application" %{luciusername} 2> /dev/null
exit 0

%post
/sbin/chkconfig --add "%{luciservice}" || :

%preun
if [ "$1" == "0" ]; then
    /sbin/service "%{luciservice}" stop &>/dev/null
    /sbin/chkconfig --del "%{luciservice}"
    rm -f -- "%{lucibaseconfig}".rpmsave-* || :
elif [ "$1" -ge "1" ] && [ -f "%{lucibaseconfig}" ]; then
%{breakpoints_luci_ini_fire}
fi

%postun
if [ "$1" -ge "1" ]; then
    /sbin/service "%{luciservice}" condrestart &>/dev/null || :
fi


%changelog
* Tue Mar 22 2016 Jan Pokorny <jpokorny@redhat.com> - 0.26.0-78
- Further fix for configuration logic wrt. SSL/TLS insecurities
  avoidance
- Enforce new configuration of luci self-managed certificate,
  preserving the possibly modified content in a backup file
  Related: rhbz#1156167, rhbz#1156187

* Tue Feb 23 2016 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-77
- luci: Fix handling of binary totem "secauth" attribute
  Resolves: rhbz#1285840

* Tue Feb 16 2016 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-76
- luci: Allow RRP configuration for UDPU
  Resolves: rhbz#1273954

* Tue Feb 16 2016 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-75
- luci: Support alternate timeout attributes for fence devices
  Resolves: rhbz#1255207

* Wed Jan 20 2016 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-74
- luci: Fix defaults for dlm/gfs_controld plock_ownership
  Resolves: rhbz#988945
- luci: Fix allowed values for totem/@secauth
  Resolves: rhbz#1285840

* Wed Jan 20 2016 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-73
- luci: Remove references to named_sdb
  Resolves: rhbz#1208649

* Wed Jan 13 2016 Jan Pokorny <jpokorny@redhat.com> - 0.26.0-72
- Make luci implicitly avoid SSLv2 and SSLv3 versions of the protocol,
  and also by default, disable RC4 cipher (unless overridden by user)
  at both the web browser/HTTPS (rhbz#1156167) and ricci daemon/SSL
  (rhbz#1156187) sides of communication
  Resolves: rhbz#1156167, rhbz#1156187
- Update luci self-managed certificate signature digest from sha1 to sha256
  Related: rhbz#1156167, rhbz#1156187
- Force generating luci.ini anew on update otherwise intended security
  hardenings will not take effect with luci already in use (and avoid
  respective downgrade issues, both using a mechanism already in place)
  Related: rhbz#1270958

* Wed Jan 06 2016 Jan Pokorny <jpokorny@redhat.com> - 0.26.0-71
- Prevent clickjacking (malicious use) of luci and enable enforcement
  of some more web service security mechanisms
  Resolves: rhbz#1270958

* Tue May 19 2015 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-70
- luci: Rebuild for changelog cleanup

* Tue May 19 2015 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-69
- luci: Add support for fence_emerson and fence_mpath
  Resolves: rhbz#1210683

* Tue May 05 2015 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-68
- luci: Add expand/collapse buttons for each inline resource
  Resolves: rhbz#919223
- luci: Preserve expert mode resource attributes when editing service groups
  Resolves: rhbz#1112297
- luci: Warn when config can't be set or activated
  Resolves: rhbz#1136456
- luci: Update fence_virt / fence_xvm labels
  Resolves: rhbz#1204910

* Sun Mar 08 2015 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-67
- Rebuild for new stop image
  Resolves: rhbz#1111249

* Sun Mar 08 2015 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-66
- luci: Add expand and collapse buttons for services
  Resolves: rhbz#919223
- luci: Add a "stop" service action in expert mode
  Resolves: rhbz#1111249
- luci: Don't lose nfsserver "nfspath" when not in expert mode
  Resolves: rhbz#1112297

* Wed Mar 04 2015 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-65
- luci: Add a cancel button to the services add resource dialog
  Resolves: rhbz#886526
- luci: Add support for miss_count_const
  Resolves: rhbz#917761
- luci: Add support for rrp_problem_count_threshold
  Resolves: rhbz#917773
- Luci: Indicate that shutdown_wait is ignored for postgres8 resources
  Resolves: rhbz#917781
- luci: Add support for the fence_apc cmd_prompt attr
  Resolves: rhbz#1010400
- luci: Don't let the add resource button disappear after adding a VM
  Resolves: rhbz#1100831

* Tue Mar 03 2015 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-64
- luci: Don't active new conf if any of the nodes didn't receive it
  Resolves: rhbz#1136456

* Tue Sep 02 2014 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-63
- luci: Fix editing services that VM references

* Tue Aug 26 2014 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-62
- luci: Fix editing services that VM references
- luci: Fix error in fence_lpar form
  luci: Fix issues with bind-mount resource name display
  Resolves: rhbz#1117398

* Wed Aug 13 2014 Jan Pokorny <jpokorny@redhat.com> - 0.26.0-61
- Resolve newly introduced issue with doubled Edit Fence Instance forms
  Related: rhbz#1127286 (CVE-2014-3593)

* Tue Aug 12 2014 Jan Pokorny <jpokorny@redhat.com> - 0.26.0-60
- Resolve issue with custom luci launcher upon update while luci running
  Related: rhbz#1026374

* Sun Aug 10 2014 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-59
- luci: Allow & in XML attribute values
  Resolves: rhbz#855112
- luci: Fix positioning of sort arrows
  Resolves: rhbz#919225
- luci: Allow nfsclient to be a child of nfsserver
  Resolves: rhbz#919243
- luci: Remove bad default values for startup_wait and
  luci: Remove ssh_options fields from fence agents that do
  luci: Support newly added bind-mount "name" attribute
  Resolves: rhbz#1117398

* Fri Aug 08 2014 Jan Pokorny <jpokorny@redhat.com> - 0.26.0-58
- Additional fix for regression with "extensionless" node names
  Related: rhbz#999324

* Wed Aug 06 2014 Jan Pokorny <jpokorny@redhat.com> - 0.26.0-57
- Fix luci unable to handle node name ending with recognized filetype extension
  Resolves: rhbz#999324
- Add a custom luci launcher allowing sane Python runtime + SELinux coexistence
  Resolves: rhbz#1026374
- Fix privilege escalation through cluster with specially crafted configuration
  Resolves: rhbz#1127286 (CVE-2014-3593)

* Mon Jul 28 2014 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-56
- luci: Update the fence_kdump config forms
  Resolves: rhbz#918795
- luci: Move sort arrows for resources
  Resolves: rhbz#919225
- luci: Cope better with editing services containing VM
  Resolves: rhbz#1100817
- luci: Add support for the bind-mount resource
  luci: Update fence_brocade
  luci: Add support for the reboot_on_pid_exhaustion
  luci: Remove mention of fenced skip_undefined
  luci: Add support for the postgres-8 startup_wait attr
  luci: Add the ssh_options attribute to applicable fence
  luci: Add support for the no_kill attribute of the VM
  luci: Add support for the use_findmnt attribute
  Resolves: rhbz#1117398

* Thu Jul 17 2014 Jan Pokorny <jpokorny@redhat.com> - 0.26.0-55
- Fine-tune update-downgrade-uninstall scriptlets as changed in rhbz#991575 fix
  and modify new suggested value in sysconfig file
  Related: rhbz#991575

* Mon Jun 30 2014 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-54
- luci: Add support for the IP "prefer_interface" attr
  Resolves: rhbz#917738

* Thu Jun 26 2014 Jan Pokorny <jpokorny@redhat.com> - 0.26.0-53
- Fix breakage upon update due to changes introduced with fix for rhbz#991575
  Related: rhbz#991575

* Tue Jun 24 2014 Jan Pokorny <jpokorny@redhat.com> - 0.26.0-52
- Add the ability to block weak ciphers (revisited)
  Resolves: rhbz#991575

* Mon Jun 23 2014 Jan Pokorny <jpokorny@redhat.com> - 0.26.0-51
- Add the ability to block weak ciphers
  Resolves: rhbz#991575
- Check length of secret on startup
  Resolves: rhbz#982771

* Mon Jun 23 2014 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-50
- luci: Don't remove attributes from xvm fence devs in
  Resolves: rhbz#1004011
- luci: Fix for option to completely disable rgmanager
  Resolves: rhbz#723925

* Sun Jun 22 2014 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-49
- luci: Add option to completely disable rgmanager
  Resolves: rhbz#723925
- luci: Disallow XML-unsafe characters in attribute
  Resolves: rhbz#855112
- luci: Add support for configuring missing totem
  Resolves: rhbz#917771
- luci: Add support for fence_kdump
  Resolves: rhbz#918795
- luci: Add support for sorting by columns of the
  Resolves: rhbz#919225
- luci: Don't allow nfsclient without nfsexport
  Resolves: rhbz#919243
- luci: Fix broken display on permissions page
  Resolves: rhbz#988446
- luci: Don't write type attribute for oracledb for
  Resolves: rhbz#1003062
- luci: Allow configuration of more fence_xvm attributes
  Resolves: rhbz#1004011
- luci: Fix default value for post_join_delay
  Resolves: rhbz#1004922
- luci: Update name for fence_egenera
  Resolves: rhbz#1008510
- luci: Support configuring "self_fence" attribute for
  Resolves: rhbz#1019853
- luci: Add support for the apache "httpd" attribute
  Resolves: rhbz#1061786
- luci: Add support for newly added nfsserver statdport
  Resolves: rhbz#1070760
- luci: Fix crash when config contains a globally defined
  Resolves: rhbz#1100817

* Mon Oct 14 2013 Jan Pokorny <jpokorny@redhat.com> - 0.26.0-48
- Postpone fix for luci not running after reportedly started due to missed corner-case
  Related: rhbz#877999

* Thu Sep 26 2013 Jan Pokorny <jpokorny@redhat.com> - 0.26.0-47
- Additional fix for support for missing fence devices
  Resolves: rhbz#917747

* Thu Sep 26 2013 Jan Pokorny <jpokorny@redhat.com> - 0.26.0-46
- Do not propagate "unfencing" verbatim to configuration
  Resolves: rhbz#883008
- Add a guard to enforce code validity during compilation phase
  Related: rhbz#883008

* Mon Sep 16 2013 Jan Pokorny <jpokorny@redhat.com> - 0.26.0-43
- Fix short exposure of authentication details while generating configuration file
  Resolves: rhbz#1005385 (part 1)
- Fix hidden untrusted path and "command" (callable association) injection
  Resolves: rhbz#1005385 (part 2)

* Thu Aug 29 2013 Jan Pokorny <jpokorny@redhat.com> - 0.26.0-42
- module_name parameter for fence_drac5 is optional, not required
  Resolves: rhbz#1001835
- fence_ilo denoted as HP iLO / iLO2, but the latter has a separate entry
  Resolves: rhbz#1001836

* Wed Aug 14 2013 Jan Pokorny <jpokorny@redhat.com> - 0.26.0-41
- Default syslog facility is "local4" (not "daemon")
  Resolves: rhbz#896244
- Fix cluster_version mismatch upon adding 2+ nodes
  Resolves: rhbz#978479
- Fix luci not running after /etc/init.d/luci reports that it has started
  Resolves: rhbz#877999

* Mon Aug 12 2013 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-40
- luci: Add support for TNS_ADMIN in oracle agents
  Resolves: rhbz#983693

* Mon Aug 12 2013 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-39
- luci: Make pop-up messages act like static status
  Resolves: rhbz#773491
- luci: Add support for fence_scsi 'delay' attribute
  Resolves: rhbz#883008
- Enable the ricci and modclusterd services when creating a
  Resolves: rhbz#886517
- luci: Remove useless "remove this instance" button
  Resolves: rhbz#886576
- luci: Add support for missing fence devices
  Resolves: rhbz#917747
- luci: Ask for confirmation when removing a cluster
  Resolves: rhbz#917814
- luci: Update Oracle agent configuration
  Resolves: rhbz#983693

* Wed Jul 17 2013 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-38
- luci: Make pop-up messages act like static status messages
  Resolves: rhbz#773491
- luci: Fix uncaught exception
  luci: Fix for tracebacks when no nodes can be contacted
  Resolves: rhbz#878149
- luci: Don't let anonymous users access the preferences page
  Resolves: rhbz#878960
- luci: Fix garbled error messages
  Resolves: rhbz#880363
- luci: Add support for fence device attributes
  Resolves: rhbz#883008
  Resolves: rhbz#917743

* Tue Jan 08 2013 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-37
- Revert the change that caused pop-up dialogs to be centered.
  Resolves: rhbz#773491

* Wed Dec 12 2012 John Ruemker <jruemker@redhat.com> - 0.26.0-36
- Correctly display the 'type' attribute value when editing an oracledb resource
  Resolves: rhbz#886678

* Tue Dec 11 2012 Jan Pokorny <jpokorny@redhat.com> - 0.26.0-35
- additional fix for luci support for fence_sanlock (in technical preview)

* Tue Dec 11 2012 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-33
- luci: Update unfence when renaming fence devices
  Resolves: rhbz#882995

* Tue Dec 11 2012 Jan Pokorny <jpokorny@redhat.com> - 0.26.0-32
- luci support for fence_sanlock (in technical preview)
  Resolves rhbz#877098

* Tue Dec 04 2012 Jan Pokorny <jpokorny@redhat.com> - 0.26.0-31
- luci: Cont'd fix of controller wrt. unicode
  Resolves rhbz#807344

* Mon Dec 03 2012 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-30
- luci: Fix matching of unfence blocks
  Resolves: rhbz#815666

* Thu Nov 29 2012 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-29
- luci: Fix the interaction of the force_unmount and nfsrestart checkboxes
  Resolves: rhbz#822502
- luci: Error out if max_restarts is set but not restart_expire_time is not
  luci: Fix handling of subtree options
  Resolves: rhbz#877188
- luci: Fix value for LVM self_fence
  Resolves: rhbz#877392
- Remove trailing commas that cause problems for some old
  Resolves: rhbz#881796
- luci: Audit of resource agent checkbox input
  Resolves: rhbz#881955

* Wed Nov 28 2012 Jan Pokorny <jpokorny@redhat.com> - 0.26.0-28
- luci: Cont'd fix of templates wrt. unicode
  Resolves rhbz#807344

* Wed Nov 28 2012 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-27
- luci: Add missing JS include
  Resolves: rhbz#822502

* Mon Nov 12 2012 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-21
- luci: Allow global resources to be referenced multiple times
  Resolves: rhbz#860042

* Mon Oct 15 2012 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-20
- luci: Fix label on fence_hpblade form
  Resolves: rhbz#865533

* Fri Oct 12 2012 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-19
- luci: Add support for fence_eaton_snmp
  Resolves: rhbz#865300
- luci: Add support for fence_hpblade
  Resolves: rhbz#865533

* Wed Oct 10 2012 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-18
- luci: Add back missing unfence patch
  Resolves: rhbz#815666

* Mon Oct 08 2012 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-17
- luci: Add the ability to remove users
  Resolves: rhbz#809892

* Mon Oct 08 2012 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-16
- luci: Add support for the IBM iPDU fence device
  Resolves: rhbz#740867
- luci: Center popup messages
  Resolves: rhbz#773491
- luci: Fix handling of resource and services
  luci: More fixes for resource/service/failover naming
  Resolves: rhbz#807344
- luci: Fix unfence display on node page
  Resolves: rhbz#815666
- luci: Add support for fence_ipmilan privlvl
  Resolves: rhbz#821928
- luci: Add support for nfsrestart
  Resolves: rhbz#822502
- luci: Fix double click on add existing dialog
  Resolves: rhbz#856253

* Fri Aug 31 2012 Jan Pokorny <jpokorny@redhat.com> - 0.26.0-15
- Fix bz853151 ("No object (name: translator) has been registered for this thread" due to private threading)
- Fix bz826951 (Prevent from invalid ID and IDREF values in cluster.conf)

* Thu May 17 2012 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-13
- Allow altmulticast port overlap and address overlap as long as both
  don't overlap the primary channel's values.

* Thu May 17 2012 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-12
- Fix the handling of power wait for fence_intelmodular

* Mon May 14 2012 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-11
- Fix bz820402 (fence_ifmib and fence_intelmodular disappeared from the fence device list)
- Additional fixes for the RRP configuration interface.

* Mon Apr 09 2012 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-10
- Additional fixes for bz772314 (The ability to add RHEL6 luci non-root users as root user)

* Fri Mar 16 2012 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-9
- Additional fix for bz740835 ([RFE] Better handling of Prioritized/Priority fields in failover domain configuration)

* Fri Mar 16 2012 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-8
- Fix bz803398 (Luci shows incorrect verbosity level for sqlalchemy logging facility)
- Fix bz801491 (A global resource with "." in the name of resource will throw an error in luci)

* Wed Mar 14 2012 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-7
- Additional fix for bz690621 (Luci Debug options for end users to enable)

* Tue Mar 06 2012 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-6
- Fix bz800239 (Add support for KVM --tunneled migration option in vm.sh resource script)

* Mon Mar 05 2012 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-5
- Update the fix for bz786584 per the latest updates to the condor resource agent.

* Fri Feb 24 2012 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-4
- Additional fix for bz749668 (Invalid fence configuration causes luci database corruption)
- Fix for bz796731 (Error 500 from luci when try to edit a Service)

* Fri Feb 17 2012 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-3
- Fix bz690621 (Luci Debug options for end users to enable)

* Tue Feb 14 2012 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-2
- Fix bz786584 (condor_schedd Resource Agent integration)

* Mon Jan 23 2012 Ryan McCabe <rmccabe@redhat.com> - 0.26.0-1
- Rebase to latest upstream version. This pulls in fixes for:
 - bz690621 ([RFE]Luci Debug options for end users to enable)
 - bz704978 ([RFE] UI: Make it easier to tell which resource a “Add a child resource” button belongs to.)
 - bz707471 ([RFE] Make reboot icon more obvious)
 - bz755092 (Luci does not expose the force_unmount option for filesystem resources)
 - bz740835 ([RFE] Better handling of Prioritized/Priority fields in failover domain configuration)
 - bz744048 ([RFE] A confirmation box before removing clustered services from conga.)
 - bz749668 (Invalid fence configuration causes luci database corruption)
 - bz758821 (cman and corosync RRP handling are not consistent and needs improvements)
 - bz768406 (The "monitor_link" ip attribute default is backwards)
 - bz772314 (The ability to add RHEL6 luci non-root users as root user)

* Tue Oct 11 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-32
- Additional cleanups for dialogs that were not reset properly when closed.

* Wed Oct 05 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-31
- Additional fix for bz705884 (luci chokes on working cluster.conf line)
- Fix to mitigate SELinux issues (bz737635)

* Tue Sep 27 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-30
- Additional fix for bz639121 (Lightbox dialog state is not reset when the dialog is closed)
- Additional fix for bz718355 (Logging feature in Luci not working as expected)
- Additional fix for bz599074 ("Use same password for all nodes" doesn't work.)

* Tue Sep 20 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-29
- Add a note about the implications of creating, deleting, and editing
  service groups on the admin page.

* Mon Sep 19 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-28
- Make sure cluster permission database objects are created properly
  after a cluster is destroyed, then recreated.

* Fri Sep 16 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-27
- Additional fixes for bz522005

* Fri Sep 16 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-26
- Additional fixes for bz522005

* Thu Sep 15 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-25
- Fix bz733084 (Cleared options are not saved correctly in Virtual Machine services)
- Additional fixes for bz522005

* Thu Sep 08 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-24
- Fix a regression introduced by the fix for bz522005

* Tue Sep 06 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-23
- Revert bz703574-2.patch as there is no /usr/bin/sqlite on RHEL6.

* Tue Sep 06 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-22
- Fix bz729730 (Windows 7 IE 8 will fail with error opening url for luci cluster management)
- Fix for bz522005 that re-enables the warning added by bz671285

* Mon Aug 22 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-21
- Fix bz522005 (improve upon existing luci user access controls/roles)
- Additional fix for bz703574

* Fri Aug 19 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-20
- Fix bz703574 (Luci Configuration Backup and Restore)
- Fix bz639121 (Lightbox dialog state is not reset when the dialog is closed)
- Fix bz643488 (UI: inconsistent lower/upper casing)
- Fix bz671285 (And warning text to Luci UI about relying on UI w/o core understanding of clustering)

* Mon Aug 15 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-19
- Fix bz718355 (Logging feature in Luci not working as expected)
- Additional fix for bz632536 (luci UpgradeTest-selinux Test)
- Fix bz664036 ([RFE] Conga should ask for confirmations before executing certain destructive operations)

* Mon Jul 04 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-18
- Fix bz705072 (Support new fence_vmware agent configuration)
- Fix bz718355 (Logging feature in Luci not working as expected)
- Fix bz632536 (luci UpgradeTest-selinux Test)
- Fix bz705884 (luci chokes on working cluster.conf line)

* Mon Jun 27 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-17
- Fix bz707918 (Luci doesn't allow subsequent service changes when non global filesystem resource is added)

* Mon Jun 27 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-16
- Fix bz705111 (When editing a failover domain without restricted/prioritized, adding a node has no effect)
- Fix bz714285 (Migration of VMs doesn't work from luci GUI)

* Mon Jun 13 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-15
- Fix bz711625 (Unable to create a cluster of KVM guests)

* Mon Jun 13 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-14
- Fix bz711625 (Unable to create a cluster of KVM guests)

* Tue Apr 12 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-13
- More fixes for bz617586 (Implement progress dialog for long-running operations)
- More fixes for bz616239 (Need option to completely destroy cluster)
- More fixes for bz557234 ([RFE] luci update to handle private network/hostnames for cluster create/config)

* Wed Apr 06 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-12
- Fix bz617587 (Luci doesn't display underlying errors)
- Fix bz617586 (Implement progress dialog for long-running operations)

* Mon Apr 04 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-11
- Additional fix for bz613871 (luci should not give ungraceful error messages when encountering fence devices that it does not recognize/support)

* Mon Mar 28 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-10
- Fix possible exception path in the luci cluster model object related to bz624558 (replace broadcast option with udpu)
- Correct duplication of the fence brocade menu item in the fence devices section related to bz681506 (readd urgently fence_brocade to the list of shipped fence_agents in luci)

* Thu Mar 17 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-9
- Fix bz639120 (Create "expert" user mode)

* Thu Mar 17 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-8
- Fix bz682843 (luci still tries to setup obsolete smb.sh Resource)

* Fri Mar 04 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-7
- Fix bz680173 (Add support for DRBD resource agent in luci)

* Wed Mar 02 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-6
- Fix bz681506 (readd urgently fence_brocade to the list of shipped fence_agents in luci)

* Thu Feb 24 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-5
- Fix bz678424 (can't add node to existing cluster)

* Mon Feb 21 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-4
- Fix bz678366 (fence management not fully functional)

* Fri Feb 04 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-3
- Fix bz659014 (Luci returns an Error 500 when accessing node configuration with FQDN names)

* Fri Feb 04 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-2
- Fix bz616239 (Need option to completely destroy cluster)
- Fix bz624558 (replace broadcast option with udpu)
- Fix bz666971 (Disable updates to static routes by RHCS IP tooling)
- Fix bz605932 (Missing "reset to defaults" button in qdisk configuration)
- Fix bz639123 (Disable action buttons when no nodes are selected)

* Mon Jan 17 2011 Ryan McCabe <rmccabe@redhat.com> - 0.23.0-1
- Fix bz622562 (Need to add support for unfencing conf. generation for SAN fencing agents and fence_scsi)
- Fix bz472972 (Separate the Oracle 10g Failover Instance in Conga to two resources called "Oracle Instance" and "Oracle Listener")
- Fix bz557234 (luci update to handle private network/hostnames for cluster create/config)
- Fix bz600078 (Warn about qdisk use for certain configurations)
- Fix bz624716 (luci displays misleading error status on initial cluster configuration pages)
- Fix bz633983 (Luci does not handle parameter "nodename" related to fence_scsi fence agent correctly)
- Fix bz536841 (Need ability to change number of votes for a node through luci)
- Fix bz600057 (Fix node uptime display)
- Fix bz613871 (luci should not give ungraceful error messages when encountering fence devices that it does not recognize/support)
- Fix bz618701 (Spaces in cluster name confuse luci)
- Fix bz620343 (Consider renaming "Services" to "Service Groups")
- Fix bz620373 (Consider changing the tab order)
- Fix bz620377 (Drop-down menus do not remember the selection)
- Fix bz632344 (Enable centralized logging configuration via Luci)
- Fix bz636267 ("Update" buttons at "Fence Devices" tab do effectively nothing)
- Fix bz636300 (Egenera fence agent: specifying username not arranged correctly)
- Fix bz639107 (Add luci support for configuring fence_rhev)
- Fix bz639124 (Reconcile local database with changes in cluster membership made outside of luci)
- Fix bz613155 (running luci init script as non-root user results in traceback)
- Fix bz614963 (Python 2.6 deprecation of BaseException.message)
- Fix bz637223 (Cisco UCS Fencing Agent)
- Fix bz643488 (inconsistent er/upper casing)
- Fix bz639111 (Support configuration of non-critical resources)
- Resolves: bz622562 bz472972 bz557234 bz600078 bz624716 bz633983 bz536841 bz600057 bz613871 bz618701 bz620343 bz620373 bz620377 bz632344 bz636267 bz636300 bz639107 bz639124 bz613155 bz614963 bz637223 bz643488 bz639111

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

* Tue Jul 27 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-10
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

* Fri May 28 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-1
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
