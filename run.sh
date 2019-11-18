#!/bin/bash

clean () {
    OLD_CONTAINER=$(docker container ls --filter='name=nps3bkp' --quiet )
    docker kill $OLD_CONTAINER
    docker container prune -f --filter='name=nps3bkp'
}

build() {
    docker build --rm -f "Dockerfile" -t nagios-plugins-s3-backup:latest .
}

create() {
    CONTAINER=$(docker create -p 8080:8080 --name=nps3bkp nagios-plugins-s3-backup)
    docker cp ~/.aws/config $CONTAINER:/root/.aws/
    docker cp ~/.aws/credentials $CONTAINER:/root/.aws/
}

start() {
    CONTAINER=$(docker ps -a --format "{{.Names}}" --filter='name=nps3bkp')
    docker start -i $CONTAINER &
}

test(){
    COUNTER=0
while [ $(docker ps | wc -l) -le 1 ] && [COUNTER -le 20]
do
    docker ps
    echo "waiting for docker start"
    COUNTER=$((COUNTER +1))
    sleep 1
done

COUNTER=0
curl http://127.0.0.1:8080
while [ $? -ne 0 ] && [COUNTER -le 20]
do
    sleep 1
    COUNTER=$((COUNTER +1))
    curl http://127.0.0.1:8080
done
}

describe () {
    CONTAINER=$(docker ps -a --format "{{.Names}}" --filter='name=nps3bkp')
    docker container ls --all
    docker inspect $CONTAINER
}

kill () {
    CONTAINER=$(docker ps --format "{{.Names}}" --filter='name=nps3bkp')
    docker kill $CONTAINER
}

prune () {
    docker container prune -f
}

"$@"