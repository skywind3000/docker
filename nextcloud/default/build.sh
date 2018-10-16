#! /bin/sh

docker rmi skywind3000/nextcloud:require 2> /dev/null
docker build -t skywind3000/nextcloud:require .

