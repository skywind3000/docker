#! /bin/sh

cd /var/www/nextcloud
sudo -u www-data php occ maintenance:update:htaccess
