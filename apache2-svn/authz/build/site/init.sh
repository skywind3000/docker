#! /bin/sh

# initialize directories
mkdir -p /var/lib/backup 2> /dev/null
mkdir -p /var/lib/svn/logs 2> /dev/null

chown www-data:www-data /var/lib/backup
chown www-data:www-data /var/lib/svn/logs

echo "$SVN_BACKUP" > /var/lib/svn/backup.txt
touch /var/lib/svn/conf/davsvn.passwd
chown www-data:www-data /var/lib/svn/conf/davsvn.passwd

rm -rf /etc/cron.d/*

# install cron task for auto auth
if [ -n "$SVN_AUTOAUTH" ]; then
	SCRIPT='/var/lib/site/script/svnauth.py'
	CONFIG='/var/lib/site/etc/svnauth.json'
	FILE='/etc/cron.d/svnauth'
	echo "*/$SVN_AUTOAUTH * * * *   www-data   /usr/bin/python $SCRIPT $CONFIG" > $FILE
fi

# install cron task for backup
if [ -n "$SVN_BACKUP" ]; then
	FILE='/etc/cron.d/svnback'
	echo "$SVN_BACKUP" > /var/lib/svn/conf/backup.txt
	echo '30 2 * * 1-6  www-data   /usr/bin/python /var/lib/site/script/backup.py inc $(cat /var/lib/svn/conf/backup.txt)' > $FILE
	echo '30 2 * * 0    www-data   /usr/bin/python /var/lib/site/script/backup.py dump $(cat /var/lib/svn/conf/backup.txt)' >> $FILE
fi

service cron restart > /dev/null


