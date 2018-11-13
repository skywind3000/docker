FROM skywind3000/debian:init
MAINTAINER skywind3000 "https://github.com/skywind3000"

ENV INIT_STOP_WAIT 0

RUN \
	apt-get install -y --no-install-recommends --no-install-suggests tomcat8 && \
	ln -s /etc/init.d/tomcat8 /usr/local/etc/rc.d/S10-tomcat8 && \
	ln -s /etc/init.d/tomcat8 /usr/local/etc/rc.d/K10-tomcat8 



