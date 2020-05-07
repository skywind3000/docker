#! /bin/sh

cd /var/www/nextcloud
sudo -u www-data php occ maintenance:update:htaccess
touch /var/www/nextcloud/config/CAN_INSTALL
chown www-data:www-data /var/www/nextcloud/config/CAN_INSTALL
