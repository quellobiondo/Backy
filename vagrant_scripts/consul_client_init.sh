#!/usr/bin/env bash

docker rm consul_client > /dev/null

echo "Activating consul client"
docker run -d --net=host -e 'CONSUL_LOCAL_CONFIG={"leave_on_terminate": true}' \
--name consul_client consul agent -bind=$1 \
-retry-join=$2