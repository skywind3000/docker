FROM skywind3000/debian:stretch
MAINTAINER skywind3000 "https://github.com/skywind3000"

COPY build /tmp/build

RUN chmod -R 755 /tmp/build/script/*
RUN run-parts --report --exit-on-error /tmp/build/script && rm -rf /tmp/build

EXPOSE 22
EXPOSE 80

CMD ["/usr/local/bin/run-apache2.sh"]



