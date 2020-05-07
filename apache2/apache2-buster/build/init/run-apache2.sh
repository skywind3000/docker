#! /bin/bash

# Init vars
if [ -z "$SERVICE_APACHE_OPTS"  ]; then 
	SERVICE_APACHE_OPTS=""
fi

# Apache gets grumpy about PID files pre-existing
rm -f /var/run/apache2/apache2*.pid

# change uid
if [ -n "$PUID" ]; then
	usermod -o -u "$PUID" www-data
fi

# change gid
if [ -n "$PGID" ]; then
	groupmod -o -g "$PGID" www-data
fi

# run memcached
if [ -n "$MEMCACHED_ENABLE" ]; then
	/usr/bin/memcached -d \
		-m "${MEMCACHED_MEM:-64}" \
		-p "${MEMCACHED_PORT:-11211}" \
		-u "${MEMCACHED_USER:-www-data}" \
		-l "${MEMCACHED_HOST:-127.0.0.1}"
fi

# run initialize scripts
/bin/sh /usr/local/etc/initz.rc execute

# start apache
source /etc/apache2/envvars
exec apache2 -DFOREGROUND -DAPACHE_LOCK_DIR $SERVICE_APACHE_OPTS


