#! /bin/sh

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


