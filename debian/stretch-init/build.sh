#! /bin/sh

docker rmi skywind3000/debian:init 2> /dev/null
docker build -t skywind3000/debian:init .

