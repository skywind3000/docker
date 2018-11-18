#! /bin/sh


create_ssl_cert() {
	openssl req -new -x509 -days 36500 -nodes -out "$1" -keyout "$2" \
			-subj "/C=US/CN=docker/O=docker.com" 
	if [ -e "$2" ]; then
		chmod 640 "$2" 2> /dev/null
		chown root:ssl-cert "$2" 2> /dev/null
	 fi
}

check_self() {
	F1=/etc/ssl/update/ssl-cert.pem
	F2=/etc/ssl/update/ssl-cert.key
	[ -d /etc/ssl/update ] || mkdir -p /etc/ssl/update 2> /dev/null
	if [ -e "$F1" ] && [ -e "$F2" ]; then
		return
	fi
	echo "Generate $F1"
	create_ssl_cert "$F1" "$F2" 2> /dev/null
}

check_snake() {
	F1=/etc/ssl/certs/ssl-cert-snakeoil.pem
	F2=/etc/ssl/private/ssl-cert-snakeoil.key
	if [ -e "$F1" ] && [ -e "$F2" ]; then
		return
	fi
	if [ -x "/usr/sbin/make-ssl-cert" ]; then
		echo "Generate default snakeoil"
		/usr/sbin/make-ssl-cert generate-default-snakeoil 2> /dev/null
	fi
}

check_self
check_snake

