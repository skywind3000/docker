FROM skywind3000/apache2-svn:default
MAINTAINER skywind3000 "https://github.com/skywind3000"

COPY build /tmp/build

RUN \
		chmod -R 755 /tmp/build/script/* && \
		run-parts --report --exit-on-error /tmp/build/script && \
		rm -rf /tmp/build

EXPOSE 443
EXPOSE 442

CMD ["/usr/local/bin/run-apache2-svn.sh"]



