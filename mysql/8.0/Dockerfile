FROM skywind3000/debian:stretch-init

# add our user and group first to make sure their IDs get assigned consistently, regardless of whatever dependencies get added
RUN groupadd -r mysql && useradd -r -g mysql mysql

RUN apt-get update && apt-get install -y --no-install-recommends gnupg dirmngr 

# add gosu for easy step-down from root
ENV GOSU_VERSION 1.7
COPY gosu.bin /usr/local/bin/ 
RUN set -x \
	&& mv /usr/local/bin/gosu.bin /usr/local/bin/gosu \
	&& chmod +x /usr/local/bin/gosu \
	&& gosu nobody true 

RUN mkdir /docker-entrypoint-initdb.d

RUN apt-get update && apt-get install -y --no-install-recommends \
# for MYSQL_RANDOM_ROOT_PASSWORD
		pwgen \
# for mysql_ssl_rsa_setup
		openssl \
# FATAL ERROR: please install the following Perl modules before executing /usr/local/mysql/scripts/mysql_install_db:
# File::Basename
# File::Copy
# Sys::Hostname
# Data::Dumper
		lsb-release \
		perl

RUN set -ex; \
	cd /tmp; \
	export DEBIAN_FRONTEND=noninteractive; \
	wget https://repo.mysql.com/mysql-apt-config_0.8.10-1_all.deb; \
	dpkg -i mysql-apt-config_0.8.10-1_all.deb; \
	apt-get update

ENV MYSQL_MAJOR 8.0
ENV MYSQL_VERSION 8.0.13-1debian9

# RUN echo "deb http://repo.mysql.com/apt/debian/ stretch mysql-${MYSQL_MAJOR}" > /etc/apt/sources.list.d/mysql.list

# the "/var/lib/mysql" stuff here is because the mysql-server postinst doesn't have an explicit way to disable the mysql_install_db codepath besides having a database already "configured" (ie, stuff in /var/lib/mysql/mysql)
# also, we set debconf keys to make APT a little quieter
RUN { \
		echo mysql-community-server mysql-community-server/data-dir select ''; \
		echo mysql-community-server mysql-community-server/root-pass password ''; \
		echo mysql-community-server mysql-community-server/re-root-pass password ''; \
		echo mysql-community-server mysql-community-server/remove-test-db select false; \
	} | debconf-set-selections \
	&& apt-get update && apt-get install -y mysql-community-client="${MYSQL_VERSION}" mysql-community-server-core="${MYSQL_VERSION}"  \
	&& rm -rf /var/lib/mysql && mkdir -p /var/lib/mysql /var/run/mysqld \
	&& chown -R mysql:mysql /var/lib/mysql /var/run/mysqld \
# ensure that /var/run/mysqld (used for socket and lock files) is writable regardless of the UID our mysqld instance ends up having at runtime
	&& chmod 777 /var/run/mysqld

VOLUME /var/lib/mysql
# Config files
COPY config/ /etc/mysql/
COPY mysql.sh /etc/init.d
COPY init-mysql.sh /usr/local/etc/rc.d/init-mysql.sh

RUN \
		set -ex; \
		mv /etc/init.d/mysql.sh /etc/init.d/mysql; \
		chmod 755 /etc/init.d/mysql; \
		ln -s /etc/init.d/mysql /usr/local/etc/rc.d/S05-mysql; \
		ln -s /etc/init.d/mysql /usr/local/etc/rc.d/K20-mysql; \
		echo ". /etc/mysql/setup_password.sh" >> /usr/local/etc/rc.d/I01-mysql; \
		echo "/bin/bash /usr/local/etc/rc.d/init-mysql.sh mysqld" >> /usr/local/etc/rc.d/I01-mysql; \
		chmod 755 /usr/local/etc/rc.d/init-mysql.sh; \
		apt-get clean


EXPOSE 3306 33060


