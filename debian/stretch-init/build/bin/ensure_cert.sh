#! /bin/sh

CERT_S="$1"
CERT_K="$2"

[ -n "$3" ] && CERT_N="$3" || CERT_N="unknow"
[ -n "$4" ] && CERT_D="$4" || CERT_D="unknow"

if [ -f "$CERT_S" ] && [ -f "$CERT_K" ]; then
	exit
fi

openssl req -new -x509 -days 36500 -nodes -out "$CERT_S" -keyout "$CERT_K" \
	    -subj "/C=US/CN=$CERT_N/O=$CERT_D"
