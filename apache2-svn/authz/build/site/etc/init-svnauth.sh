#! /bin/sh

# initialize directories
mkdir -p /var/lib/backup 2> /dev/null
mkdir -p /var/lib/svn/logs 2> /dev/null

chown www-data:www-data /var/lib/backup
chown www-data:www-data /var/lib/svn/logs

touch /var/lib/svn/conf/davsvn.passwd
chown www-data:www-data /var/lib/svn/conf/davsvn.passwd

mkdir -p /dev/shm/svnauthz 2> /dev/null
chown -R www-data:www-data /dev/shm/svnauthz

rm -rf /etc/cron.d/*

# install cron task for auto auth
if [ -n "$SVN_AUTOAUTH" ]; then
	FILE='/etc/cron.d/svnauth'
	SCRIPT='/var/lib/site/script/svnauth.py'
	CONFIG='/var/lib/site/etc/svnauth.json'
	echo "*/$SVN_AUTOAUTH * * * *   www-data   /usr/bin/python $SCRIPT $CONFIG" > $FILE
fi

# install cron task for backup
if [ -n "$SVN_BACKUP" ]; then
	FILE='/etc/cron.d/svnback'
	SCRIPT='/var/lib/site/script/backup.py'
	[ -n "$SVN_BACKUP_HOUR" ] && HOUR="$SVN_BACKUP_HOUR" || HOUR=2
	[ -n "$SVN_BACKUP_MINUTE" ] && MINUTE=$SVN_BACKUP_MINUTE || MINUTE=30
	echo "$MINUTE $HOUR * * 1-6  www-data   /usr/bin/python $SCRIPT inc \"$SVN_BACKUP\"" > $FILE
	echo "$MINUTE $HOUR * * 0    www-data   /usr/bin/python $SCRIPT dump \"$SVN_BACKUP\"" >> $FILE
fi

service cron restart > /dev/null


