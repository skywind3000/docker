#! /bin/sh

if [ $(whoami) != 'root' ]; then
	if [ $(whoami) != 'www-data' ]; then
			echo "you must be root or www-data to start this script"
			exit 1
	fi
fi

NAME="$1"

if [ -z "$NAME" ]; then
	echo "usage: svn-create.sh [NAME]"
	exit 1
fi

if [ -d "/var/lib/svn/repos/$NAME" ]; then
	echo "error: /var/lib/svn/repos/$NAME exists"
	exit 2
fi

echo "Creating $NAME: "

cd /var/lib/svn/repos
svnadmin create "$NAME"
cp /var/lib/site/etc/pre-commit "$NAME/hooks"
chmod 755 "$NAME/hooks/pre-commit"
chown -R www-data:www-data "$NAME"

rm -rf /tmp/svntmp
mkdir -p /tmp/svntmp 2> /dev/null
cd /tmp/svntmp

svn checkout "file:///var/lib/svn/repos/$NAME"
cd "$NAME"

mkdir authz
echo "[/]" > authz/access.ini
echo "* = r" >> authz/access.ini
svn add authz
svn commit -m "initialize /authz/access.ini in $NAME"
rm -rf /tmp/svntmp

cd "/var/lib/svn/repos/"
chown -R www-data:www-data "$NAME"

echo "$NAME succeeded !!"


exit 0


