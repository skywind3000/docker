#! /bin/sh

docker rmi skywind3000/gitbucket:https 2> /dev/null
docker build -t skywind3000/gitbucket:https .

