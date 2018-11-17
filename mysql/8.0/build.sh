#! /bin/sh

docker rmi skywind3000/mysql:8.0 2> /dev/null
docker build -t skywind3000/mysql:8.0 .

