#! /bin/bash

[ -d /var/lib/svn ] || mkdir -p /var/lib/svn 2> /dev/null
[ -d /var/lib/svn/conf ] || mkdir -p /var/lib/svn/conf 2> /dev/null
[ -d /var/lib/svn/repos ] || mkdir -p /var/lib/svn/repos 2> /dev/null
[ -d /var/lib/svn/history ] || mkdir -p /var/lib/svn/history 2> /dev/null
[ -d /var/lib/svn/backup ] || mkdir -p /var/lib/svn/backup 2> /dev/null

chown www-data:www-data /var/lib/svn
chown www-data:www-data /var/lib/svn/*

exec bash /usr/local/bin/run-apache2.sh
