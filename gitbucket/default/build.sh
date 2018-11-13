#! /bin/sh

docker rmi skywind3000/gitbucket:default 2> /dev/null
docker build -t skywind3000/gitbucket:default .

