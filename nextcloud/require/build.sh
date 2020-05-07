#! /bin/sh

docker rmi skywind3000/nextcloud:buster-require 2> /dev/null
docker build -t skywind3000/nextcloud:buster-require .

