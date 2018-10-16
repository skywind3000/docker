FROM skywind3000/apache2:stretch
MAINTAINER skywind3000 "https://github.com/skywind3000"

COPY build /tmp/build
COPY nextcloud-*.tar.bz2 /tmp/nextcloud-latest.tar.bz2

RUN chmod -R 755 /tmp/build/script/*
RUN run-parts --report --exit-on-error /tmp/build/script && rm -rf /tmp/build

EXPOSE 443
EXPOSE 442

CMD ["/usr/local/bin/run-apache2-svn.sh"]



