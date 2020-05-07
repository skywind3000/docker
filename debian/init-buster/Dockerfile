FROM skywind3000/debian:buster
MAINTAINER skywind3000 "https://github.com/skywind3000"

ENV INIT_STOP_WAIT 1

COPY build /tmp/build

RUN \
	chmod -R 755 /tmp/build/script/* && \
	run-parts --report --exit-on-error /tmp/build/script && \
	rm -rf /tmp/build

CMD ["/usr/local/etc/initz.rc"]


