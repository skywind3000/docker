FROM skywind3000/nextcloud:require
MAINTAINER skywind3000 "https://github.com/skywind3000"

COPY build /tmp/build

RUN chmod -R 755 /tmp/build/script/*
RUN run-parts --report --exit-on-error /tmp/build/script && rm -rf /tmp/build

EXPOSE 443

VOLUME ["/var/www/nextcloud/config", "/var/www/nextcloud/data"]

CMD ["/usr/local/bin/run-apache2.sh"]



