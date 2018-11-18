#! /bin/bash

# Init vars
if [ -z "$SERVICE_APACHE_OPTS"  ]; then 
	SERVICE_APACHE_OPTS=""
fi

# Apache gets grumpy about PID files pre-existing
rm -f /var/run/apache2/apache2*.pid

# run initialize scripts
/bin/sh /usr/local/etc/initz.rc execute

# start apache
source /etc/apache2/envvars
exec apache2 -DFOREGROUND -DAPACHE_LOCK_DIR $SERVICE_APACHE_OPTS


