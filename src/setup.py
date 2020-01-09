# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages, Extension
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages, Extension

from os.path import (join as path_join, basename as path_basename,
                     dirname as path_dirname, normpath as path_norm,
                     isabs as path_isabs)
import sys
from shutil import copy, copymode
from distutils.cmd import Command
from distutils.errors import DistutilsSetupError
from distutils.command.build import build
from distutils.command.install import install
from collections import Callable



DEBUG = False
DBGPFX = str(__file__)

#
# Custom machinery extending setuptools/distutils with mechanism
# for parameterization (mainly paths) and even content of these files
#

def setup_pkg_prepare(pkg_name, pkg_prepare_options=[]):

    class pkg_prepare(Command):
        DEV_SWITCH = 'develop'
        description = ("Prepare specified files, i.e. substitute some values "
                       "(works as a subcommand for ``build'' and ``install'' "
                       "and can also mimic enhanced ``develop'' using %s)"
                       % DEV_SWITCH)
        user_options = [
            (key + "=", None, "specify " + help + " for " + pkg_name)
            for key, help in pkg_prepare_options
        ]
        user_options.append((DEV_SWITCH, None, "mimics ``develop'' command "
                             "(to be used only with standalone ``pkg_prepare'')"))
        boolean_options = [DEV_SWITCH]
        needs_any_opt = ['package_data', 'data_files', 'buildonly_files']
        needs_always_opts = ['pkg_params']

        @classmethod
        def get_name(cls):
            return cls.__name__

        @classmethod
        def inject_cmdclass(cls, **orig_classes):
            cmdclass = {}
            for name, injectclass in orig_classes.iteritems():
                cmdclass[name] = cls._inject(name, injectclass)
            cmdclass[cls.get_name()] = cls
            return cmdclass

        @classmethod
        def _inject(cls, name, orig_cls):
            orig_sub_commands = orig_cls.sub_commands[:]
            if name == "install":
                # Change predicate telling whether to run ``install_data''
                # subcommand within ``install'' command to always return true
                for i, (subcmd, predicate) in enumerate(orig_sub_commands):
                    if subcmd == "install_data":
                        orig_sub_commands[i] = (subcmd, lambda this: True)

            class new_cls(orig_cls):
                sub_commands = [(
                    cls.get_name(),
                    lambda cmd:  # When is reasonable to run this subcommand
                        len(set(cls.needs_any_opt).intersection(
                            cmd.distribution.get_option_dict(cls.get_name())
                        )) != 0
                        and len(set(cls.needs_always_opts).difference(
                            cmd.distribution.get_option_dict(cls.get_name())
                        )) == 0
                )] + orig_sub_commands
                description = (orig_cls.description + " (modified: "
                               "additionally prepare some files for %s, "
                               "i.e. substitute some values)" % pkg_name)

            return new_cls

        def __init__(self, dist):
            self.pkg_options = map(
                lambda (key,_,__): key.split('=', 1)[0],
                self.user_options
            )
            Command.__init__(self, dist)

        def initialize_options(self):
            # Parameters we want to obtain via setup.cfg, command-line
            # arguments etc. must be prepared as attributes of this object
            if DEBUG: print (DBGPFX + "\tinitialize_options")
            for key in (self.pkg_options + self.needs_any_opt
                        + self.needs_always_opts):
                setattr(self, key, None)
            setattr(self, self.DEV_SWITCH, 0)

        def finalize_options(self):
            # Obtained parameters are all moved to ``self.pkg_params'' dict
            if DEBUG: print (DBGPFX + "\tfinalize_options")
            for key in self.pkg_options:
                value = getattr(self, key)
                if value is None:
                    raise DistutilsSetupError, \
                          ("Missing `%s' value (specify it on command-line"
                           " or in setup.cfg)" % key)
                else:
                    self.pkg_params[key] = value
            # Evaluate all functions within pkg_params (semi-lazy evaluation)
            for key, value in self.pkg_params.iteritems():
                if hasattr(value, "__call__") or isinstance(value, Callable):
                    self.pkg_params[key] = value(self.pkg_params)

        def run(self):
            if DEBUG: print (DBGPFX + "\trun")
            if self.distribution.get_command_obj('install', create=False):
                # As a part of ``install'' command
                if DEBUG: print (DBGPFX + "\trun: install")
                self._pkg_prepare_install()
            elif self.distribution.get_command_obj('build', create=False):
                # As a part of ``build'' command
                if DEBUG: print (DBGPFX + "\trun: build")
                self._pkg_prepare_build()
            elif getattr(self, self.DEV_SWITCH, 0):
                # Mimic ``develop'' command over "prepared" files
                if DEBUG: print (DBGPFX + "\trun: mimic develop")
                self._pkg_prepare_build()
                self._pkg_prepare_install()
                self.run_command('install_data')
                self.run_command('develop')
            else:
                from distutils import log
                log.info("``pkg_name'' command used with no effect")

        def _pkg_prepare_build(self):
            for pkg_name, filedefs in self.package_data.iteritems():
                dst_top = self.distribution.package_dir.get('', '')
                dst_pkg = path_join(
                              dst_top,
                              self.distribution.package_dir.get(pkg_name, pkg_name)
                )
                if DEBUG: print (DBGPFX + "\tbuild dst_pkg %s" % dst_pkg)
                for filedef in filedefs:
                    self._pkg_prepare_file(
                        self.pkg_params[filedef['src']],
                        path_join(dst_pkg, self.pkg_params[filedef['dst']]),
                        filedef.get('substitute', False)
                    )
                    self.distribution.package_data[pkg_name].append(
                        self.pkg_params[filedef['dst']]
                    )
            for filedef in (self.data_files + self.buildonly_files):
                self._pkg_prepare_file(
                    self.pkg_params[filedef['src']],
                    path_join(
                        path_dirname(self.pkg_params[filedef['src']]),
                        path_basename(self.pkg_params[filedef['dst']])
                    ),
                    filedef.get('substitute', False)
                )

        def _pkg_prepare_install(self):
            for filedef in self.data_files:
                self.distribution.data_files.append((
                    path_dirname(self.pkg_params[filedef['dst']]), [
                        path_join(
                            path_dirname(self.pkg_params[filedef['src']]),
                            path_basename(self.pkg_params[filedef['dst']])
                        ),
                    ]
                ))
                if DEBUG:
                    print (DBGPFX + "\tinstall data_files: %s"
                           % self.distribution.data_files)

        def _pkg_prepare_file(self, src, dst, substitution=False):
            if path_isabs(dst):
                # This function should not attempt doing dangerous things
                # and absolute file destination path is not expected anyway
                # (copying to destination paths is handled by ``install'')
                raise DistutilsSetupError, \
                      ("Unexpected attempt to copy file %s to absolute"
                       " location %s" % (src, dst))
            if substitution:
                if DEBUG:
                    print (DBGPFX + "\tSubstituting strings while copying %s -> %s"
                           % (src, dst))
                if self.dry_run:
                    return
                try:
                    with open(src, "r") as fr:
                        with open(dst, "w") as fw:
                            content=fr.read()
                            for key in filter(
                                lambda k: not k.startswith("_")
                                          and k not in self.boolean_options,
                                self.pkg_params.iterkeys()
                            ):
                                if DEBUG:
                                    print (DBGPFX + "\tReplace %s -> %s"
                                           % ('@' + key.upper() + '@', self.pkg_params[key]))
                                content = content.replace(
                                              '@' + key.upper() + '@',
                                              self.pkg_params[key]
                                )
                            fw.write(content)
                    copymode(src, dst)
                except IOError, e:
                    raise DistutilsSetupError, str(e)
            else:
                if DEBUG:
                    print (DBGPFX + "\tSimply copying %s -> %s" % (src, dst))
                if self.dry_run:
                    return
                try:
                    copy(src, dst)
                    copymode(src, dst)
                except IOError, e:
                    raise DistutilsSetupError, str(e)
    # class pkg_prepare

    return pkg_prepare


# =========================================================================

pkg_name = 'luci'
pkg_root = path_norm('')
sys.path = sys.path[:1] + [pkg_root] + sys.path[1:]
pkg = __import__(pkg_name, globals(), locals(), [
                     'authors',
                     'fancy_name',
                     'description',
                     'licence',
                     'version',
                     'author',
                     'email',
                     'version_info',
                     'config_template',
                 ], -1)

# Setup of ``pkg_prepare'' subcommand provided with the items to form options
# for this command;
# each such option requires to be specified (either via command-line or via
# setup.cfg) for correct invocation of this subcommand and after these
# specifications are proceeded, resulting (key, defined value) pairs are added
# into ``pkg_params'' passed as an option to this command in ``setup()''
# so they can be used for string substitutions as well
pkg_prepare = setup_pkg_prepare(pkg_name, [
    # Important parameters for luci and start of its service
    ('username'        , "daemon user"),
    ('groupname'       , "daemon group"),
    ('port'            , "port"),
    # State directory for luci + nested dirs and files
    ('statedir'        , "state directory"),
    ('baseconfig'      , "base configuration"),
    ('certconfig'      , "certificate configuration file"),
    ('certpem'         , "certificate (PEM) file"),
    ('dbfile'          , "database file"),
    # Work files spread in the system directories
    ('runtimedatadir'  , "directory for run-time data"),
    ('cachedir'        , "cache data directory"),
    ('sessionsdir'     , "sessions data directory"),
    ('pidfile'         , "PID file"),
    ('lockfile'        , "lockfile"),
    ('logfile'         , "log file"),
    # System files (initscript and configuration files)
    ('initscript'      , "initscript file"),
    ('sysconfig'       , "configuration file coming with initscript"),
    ('launcher'        , "launcher script for luci (wrapper above paster)"),
    ('logrotateconfig' , "logrotate configuration file"),
    ('pamconfig'       , "PAM configuration file"),
    ('sasl2config'     , "Cyrus SASL configuration file"),
])

# Contains important values that are then referred to from ``package_data'',
# ``data_files'' etc. definitions within options for ``pkg_prepare'' subcommand
# in ``setup()'', and also serve for strings substituations/interpolations
# (applied to files defined within options for ``pkg_prepare'' subcommand where
# required and except for those starting with underscore)
#
# The right side can be either string or lazily evaluated function returning
# string with this dictionary (dynamically updated with the concrete values
# for parameters passed into ``setup_pkg_prepare'') as a parameter
pkg_params = {
    'pkgname'           : pkg_name,

    '__certconfig'      : path_norm("input_files/certconfig/certconfig.in"),

    '__ext_sasl2auth_h' : path_norm("extensions/sasl2auth.h.in"),
    'ext_sasl2auth_h'   : path_norm("extensions/sasl2auth.h"),

    # This depends on whether it is "developer's mode" or not
    '__configtmpl'      : lambda pkg_params:
                          "input_files/config.tmpl/config.tmpl.in"
                          + ('', '-dev')[pkg_params[pkg_prepare.DEV_SWITCH]],
    'configtmpl'        : path_join(path_norm(pkg.config_template)),

    '__initscript'      : path_norm("input_files/initscript/initscript.in"),
    '__sysconfig'       : path_norm("input_files/sysconfig/sysconfig.in"),
    '__logrotateconfig' : path_norm("input_files/logrotateconfig/logrotateconfig.in"),
    '__pamconfig'       : path_norm("input_files/pamconfig/pamconfig.in"),
    '__sasl2config'     : path_norm("input_files/sasl2config/sasl2config.in"),

    # This depends on passed "initscript" value
    'servicename'       : lambda pkg_params:
                          path_basename(pkg_params['initscript']),
    # This depends on passed "sasl2config" value (get rid of .conf extension)
    'saslappname'       : lambda pkg_params:
                          path_basename(pkg_params['sasl2config']).rsplit(".conf",1)[0],
    # This depends on passed "pamconfig" value
    'saslservice'       : lambda pkg_params:
                          path_basename(pkg_params['pamconfig']),
    # This depends on whether it is "developer's mode" or not
    'reload'            : lambda pkg_params:
                          ('', '--reload')[pkg_params[pkg_prepare.DEV_SWITCH]],
}


# =========================================================================

setup(

    # STANDARD DISTUTILS ARGUMENTS

    name=pkg.fancy_name,
    version=pkg.version,
    description='Web-based high availability administration application',
    url='https://fedorahosted.org/cluster/wiki/Luci',
    license=pkg.licence,
    author=pkg.author,
    author_email=pkg.email,
    maintainer=pkg.author.partition(", ")[0],
    maintainer_email=pkg.email.partition(", ")[0],
    download_url='http://people.redhat.com/rmccabe/luci/',
    long_description=pkg.description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: TurboGears',
        'Framework :: TurboGears :: Applications',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: System :: Clustering',
        'Topic :: System :: Systems Administration',
    ],
    keywords='luci cluster HA management',

    package_dir = {'': pkg_root},
    # ``find_packages'' provided by setuptools avoids the unconvenient
    # listing each subpackage in package hierarchy
    packages=find_packages(
        exclude=['ez_setup']
    ),
    ext_modules=[
        Extension(pkg_name + '.sasl2auth',
            libraries=['sasl2'],
            sources=['extensions/sasl2auth.c'],
            define_macros=[
                #('USE_GETOPT_CALLBACK', None)
            ],
        )
    ],
    # Following content is also duplicated (in a simplier/more declarative way)
    # in MANIFEST.in which serves for ``setup.py sdist'' command and is
    # necessary due to http://bugs.python.org/issue2279 fixed as of Python 2.7;
    # TODO: MANIFEST.in will be presumably dropped at some point in the future
    # Note: See ``package_data'' under options['pkg_prepare']
    package_data={
        pkg_name: [
            'public/css/*.css',
            'public/css/images/*.png',
            'public/favicon.ico',
            'public/images/*.gif',
            'public/images/*.png',
            'public/js/*.js',
            'templates/*.html',
            # TODO: uncomment this when ready for localization
            #'i18n/*/LC_MESSAGES/*.mo',
        ],
    },
    # Note: See ``data_files'' in options for ``pkg_prepare'' subcommand
    data_files=[],
    # Override ``build'' command handler with local specialized one
    cmdclass = dict(
        **pkg_prepare.inject_cmdclass(build=build, install=install)
    ),
    options = {
        # Options "passed" to ``pkg_prepare'' subcommand
        pkg_prepare.get_name(): dict(
            pkg_params=pkg_params,
            # In addition to standard ``package_data''
            package_data={
                pkg_name: [
                    dict(src='__configtmpl', dst='configtmpl', substitute=True),
                ],
            },
            # In addition to standard ``data_files''
            data_files=[
                dict(src='__certconfig',      dst='certconfig',      substitute=True),
                dict(src='__initscript',      dst='initscript',      substitute=True),
                dict(src='__sysconfig',       dst='sysconfig',       substitute=True),
                dict(src='__logrotateconfig', dst='logrotateconfig', substitute=True),
                dict(src='__pamconfig',       dst='pamconfig',       substitute=False),
                dict(src='__sasl2config',     dst='sasl2config',     substitute=True),
            ],
            # Similar to ``data files'' but for files used e.g. for building
            # C extensions
            buildonly_files=[
                dict(src='__ext_sasl2auth_h', dst='ext_sasl2auth_h', substitute=True),
            ],
        ),
    },


    # ADDITIONAL SETUPTOOLS ARGUMENTS

    setup_requires=[
        # Only for dealing with i18n (extracting strings etc.)
        # TODO: uncomment this when ready for localization
        # "Babel >=0.9.4",
        # Used (only passively, via its ``egg_info.writers'' entry point
        # sought by setuptools) to create paster_plugins.txt in egg-info dir
        # with the content defined in ``paster_plugins'' value
        "PasteScript >= 1.7",
    ],
    install_requires=[
        "repoze.who-friendlyform",
        "TurboGears2 >= 2.0b7",
        # Used but already required by previously stated (i.e. transitively):
        # "PasteDeploy",
        # "repoze.what",
        # "repoze.what-pylons",
        # "repoze.who",
        # "SQLAlchemy",
        # "toscawidgets >= 0.9.7.1",
        # "transaction",
        # "zope.interface",
        # "zope.sqlalchemy >= 0.4",
    ],
    # Use pure ``package_data'' value (i.e. do no use MANIFEST.ini or CVS tree);
    # see also comment by ``package data''
    include_package_data=False,

    # TODO: uncomment this when ready for tests
    #test_suite='nose.collector',
    #tests_require=['BeautifulSoup', 'WebTest'],

    # Entry points (``dynamic discovery of services and plugins'' mechanism
    # introduced by setuptools); mainly following groups of entry points are
    # required for interaction with PasteScript (related ``paster'' commands):
    #   * paste.app_install: used by ``make-config'' or ``setup-app'' commands
    #   * paste.app_factory: used by ``serve'' commands
    #
    # Note 1: ``make-config'' visits the entry point via explicitly defined
    #         package name as parameter, ``setup-app'' and ``serve'' visit it
    #         through provided ini file (``use'' value in ``app'' section)
    # Note 2: for both groups of entry points, ``main'' is a default key, but
    #         any specific can be chosen which has to be then referred to
    #         explicitly e.g. using "use = egg:pkg#specific_key" in ini file
    entry_points="""
        [paste.app_install]
        main = %(pkg_name)s.initwrappers:PylonsInstaller

        [paste.app_factory]
        main = %(pkg_name)s.config.middleware:make_app
    """ % dict(pkg_name=pkg_name),


    # OTHER ADDITIONAL ARGUMENTS

    # This is referred to from ``egg_info.writers'' entry point of PasteScript
    # (see comment by ``setup_requires'');
    # ``paster'', when invoked inside directory where this Python package was
    # installed (or "developed"), will try to find approriate entry points
    # of following packages and will enable discovered project-local commands
    # to be used (beside global commands applicable anywhere)
    paster_plugins=['PasteScript', 'Pylons', 'TurboGears2', 'tg.devtools'],

    # Babel configuration; used by ``python setup.py extract_messages''
    message_extractors={
        pkg_name: [
            ('**.py',             'python', None),
            ('templates/**.html', 'genshi', None),
            ('public/**',         'ignore', None),
        ],
    },
)
