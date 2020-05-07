FROM skywind3000/nextcloud:buster-require
MAINTAINER skywind3000 "https://github.com/skywind3000"

COPY build /tmp/build

RUN chmod -R 755 /tmp/build/script/*
RUN run-parts --report --exit-on-error /tmp/build/script && rm -rf /tmp/build

EXPOSE 443

VOLUME ["/var/www/nextcloud/config", "/var/www/nextcloud/data"]

# enable url rewrite by changing config.php and add:
#     'htaccess.RewriteBase' => '/',
# below:
#     'overwrite.cli.url' => '*****',
# and add a slash '/' after the text of 'overwrite.cli.url', finally execute:
#     nextcloud-update.sh

# memcached can be used at 127.0.0.1:11211 in the container

CMD ["/usr/local/bin/run-apache2.sh"]



