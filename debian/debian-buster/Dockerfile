FROM debian:buster

MAINTAINER skywind3000 "https://github.com/skywind3000"

COPY build /tmp/build

RUN \
	chmod -R 755 /tmp/build/script/* && \
	run-parts --report --exit-on-error /tmp/build/script && \
	rm -rf /tmp/build 

EXPOSE 22

CMD ["/sbin/init"]


