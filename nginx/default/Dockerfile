FROM skywind3000/debian:init
MAINTAINER skywind3000 "https://github.com/skywind3000"

ENV INIT_STOP_WAIT 0

COPY build /tmp/build

RUN chmod -R 755 /tmp/build/script/*
RUN run-parts --report --exit-on-error /tmp/build/script && rm -rf /tmp/build

EXPOSE 80

CMD ["/usr/local/etc/initz.rc"]



