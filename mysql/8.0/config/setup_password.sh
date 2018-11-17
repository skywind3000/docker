#! /bin/sh

if [ ! -d "/var/lib/mysql/mysql" ]; then
	if [ -z "$MYSQL_ROOT_PASSWORD" -a -z "$MYSQL_ALLOW_EMPTY_PASSWORD" -a -z "$MYSQL_RANDOM_ROOT_PASSWORD" ]; then
		echo >&2 'error: database is uninitialized and password option is not specified '
		echo >&2 '  You need to specify one of MYSQL_ROOT_PASSWORD, MYSQL_ALLOW_EMPTY_PASSWORD and MYSQL_RANDOM_ROOT_PASSWORD'
		exit 1
	fi
fi

if [ ! -z "$MYSQL_RANDOM_ROOT_PASSWORD" ]; then
	export MYSQL_ROOT_PASSWORD="$(pwgen -1 32)"
	echo "GENERATED ROOT PASSWORD: $MYSQL_ROOT_PASSWORD"
	export MYSQL_RANDOM_ROOT_PASSWORD=""
fi

FILE=/etc/mysql/debian.cnf
echo "[client]" > $FILE
echo "host=localhost" >> $FILE
echo "user=root" >> $FILE
echo "password=$MYSQL_ROOT_PASSWORD" >> $FILE
echo "socket=/var/run/mysqld/mysqld.sock" >> $FILE
echo "" >> $FILE

echo "[mysql_upgrade]" >> $FILE
echo "host=localhost" >> $FILE
echo "user=root" >> $FILE
echo "password=$MYSQL_ROOT_PASSWORD" >> $FILE
echo "socket=/var/run/mysqld/mysqld.sock" >> $FILE
echo "basedir=/usr" >> $FILE
echo "" >> $FILE


