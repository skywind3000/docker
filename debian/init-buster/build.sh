#! /bin/sh

docker rmi skywind3000/debian:buster-init 2> /dev/null
docker build -t skywind3000/debian:buster-init .

