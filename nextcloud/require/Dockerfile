FROM skywind3000/apache2:buster
MAINTAINER skywind3000 "https://github.com/skywind3000"

COPY build /tmp/build

# download from https://download.nextcloud.com/server/releases/
COPY nextcloud-*.tar.bz2 /tmp/nextcloud-latest.tar.bz2

RUN chmod -R 755 /tmp/build/script/*
RUN run-parts --report --exit-on-error /tmp/build/script && rm -rf /tmp/build

EXPOSE 443

CMD ["/usr/local/bin/run-apache2.sh"]



