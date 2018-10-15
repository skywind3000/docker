#! /bin/bash

chown www-data:www-data /var/lib/svn
chown www-data:www-data /var/lib/svn/*

exec bash /usr/local/bin/run-apache2.sh
