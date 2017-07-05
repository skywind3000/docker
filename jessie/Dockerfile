FROM debian:jessie
MAINTAINER skywind3000 "https://github.com/skywind3000"

COPY build /tmp/build
RUN chmod -R 755 /tmp/build/script/*
RUN run-parts --report --exit-on-error /tmp/build/script 

EXPOSE 22
CMD ["/sbin/init"]



