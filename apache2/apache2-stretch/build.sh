#! /bin/sh

docker rmi skywind3000/apache2:stretch 2> /dev/null
docker build -t skywind3000/apache2:stretch .

