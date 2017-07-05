#! /bin/sh

docker rmi skywind3000/jessie:163 2> /dev/null
docker build -t skywind3000/jessie:163 .

