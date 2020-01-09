#!/bin/bash
#
# Script with the purpose to ease developing and debugging of luci.
#
# packages needed (probably not exhausting):
#   gcc
#   python-devel
#   cyrus-sasl-devel

if [ "$(whoami)" != "root" ]; then
    echo "Root permissions required..."
    su -c "$0 $(whoami) $(id -gn) $@"
    exit $?
elif [ -z "$1" -o -z "$2" ]; then
    echo "You must be non-root to run this script (although it is switched" \
         "to root afterwards as some tasks require this level of permissions)"
    exit 1
fi

# Ensure we are in the same directory as this script
cd "$(dirname "$0")"


USERNAME="$1"
GROUPNAME="$2"

BUILD_ARTIFACTS=(build luci.egg-info luci/sasl2auth.so)

CONFIG_DIR=input_files/config.tmpl
CONFIG_FILE=config.tmpl.in
# This has to correspond to what is in setup.py for "developer's mode"
CONFIG_DEV_FILE=config.tmpl.in-dev
CONFIG_DEV_PATCHES=(debug_app.patch debug_logging.patch)

# These are absolute paths (just to be sure)
DEV_ROOT="$(pwd)"/dev
BASECONFIG="$DEV_ROOT"/luci.ini
CERTCONFIG="$DEV_ROOT"/cacert.config
CERTPEM="$DEV_ROOT"/host.pem
DBFILE="$DEV_ROOT"/luci.db

RUNTIMEDATADIR="$DEV_ROOT"/run
CACHEDIR="$RUNTIMEDATADIR"/cache
SESSIONSDIR="$RUNTIMEDATADIR"/sessions
PIDFILE="$DEV_ROOT"/luci.pid
LOCKFILE="$DEV_ROOT"/luci.lock
LOGFILE="$DEV_ROOT"/luci.log

SYSCONFIG="$DEV_ROOT"/luci.sysconfig


# Predicate with booleans as usual for shell (0..true, 1..false)
systemd_used() {
    rel="$(cat /etc/redhat-release 2>/dev/null)"
    fedora_rel_getter="s/Fedora release \([1-9]\+[0-9]*\).*/\1/"
    fedora_rel=$(echo "$rel" | sed "$fedora_rel_getter")
    if [ $fedora_rel -ge 15 ]; then
        return 0
    else
        return 1
    fi
}

start() {
    systemd_used
    if [ $? -eq 0 ]; then
        pushd /etc/init.d >/dev/null
        ./luci start
        popd >/dev/null
    else
        service luci start
    fi
}

stop() {
    systemd_used
    if [ $? -eq 0 ]; then
        pushd /etc/init.d >/dev/null
        ./luci stop
        popd >/dev/null
    else
        service luci stop
    fi
}

clean_dev_root() {
    rm -rf -- "$DEV_ROOT"
}

clean_build_artifacts() {
    rm -rf -- "${BUILD_ARTIFACTS[@]}"
}

clean() {
    stop
    python setup.py develop -u
    clean_dev_root
    clean_build_artifacts
}

prepare_config() {
    pushd "$CONFIG_DIR" >/dev/null
    cp -f "$CONFIG_FILE" "$CONFIG_DEV_FILE"
    cat "${CONFIG_DEV_PATCHES[@]}" | patch "$CONFIG_DEV_FILE"
    popd >/dev/null
}

prepare_dev_root() {
    mkdir "$DEV_ROOT"
    fix_ownership
}

fix_ownership() {
    chown -R $USERNAME:$GROUPNAME "$DEV_ROOT"
}

develop() {
    prepare_config
    clean_dev_root
    prepare_dev_root
    python setup.py pkg_prepare --develop              \
                    --username=$USERNAME               \
                    --groupname=$GROUPNAME             \
                    \
                    --statedir="$DEV_ROOT"             \
                    --baseconfig="$BASECONFIG"         \
                    --certconfig="$CERTCONFIG"         \
                    --certpem="$CERTPEM"               \
                    --dbfile="$DBFILE"                 \
                    \
                    --runtimedatadir="$RUNTIMEDATADIR" \
                    --cachedir="$CACHEDIR"             \
                    --sessionsdir="$SESSIONSDIR"       \
                    --pidfile="$PIDFILE"               \
                    --lockfile="$LOCKFILE"             \
                    --logfile="$LOGFILE"               \
                    \
                    --sysconfig="$SYSCONFIG"
    fix_ownership
}

run() {
    [ ! -f "$LOCKFILE" ] || stop
    [ -d "$DEV_ROOT" ] || develop
    ret=$?
    if [ $ret -eq 0 ]; then
        start
        if [ $? -eq 0 ]; then
            for i in $(seq 0 76); do echo -n "="; done
            echo
            trap true 2
            tail -f "$LOGFILE"
            for i in $(seq 0 76); do echo -n "="; done
            echo -e "\nCtrl-C interrupted the run"
            stop
            ret=$?
        else
            echo "Error encountered (start)"
            ret=67
        fi
    else
        echo "Error encountered (develop)"
        ret=68
    fi
    return $ret
}


case "$3" in
    ""|run)
        run
        ;;
    develop)
        $3
        ;;
    stop)
        $3
        ;;
    clean)
        $3
        ;;
    svc-start)
        start
        ;;
    svc-stop)
        stop
        ;;
    *)
        echo "Usage: $0 {run|develop|stop|clean|svc-start|svc-stop}"
        exit 2
    ;;
esac
exit $?
