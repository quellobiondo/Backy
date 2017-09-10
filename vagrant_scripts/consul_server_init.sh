#!/usr/bin/env bash
docker rm consul-server > /dev/null
docker run -d --name consul-server --net=host -e 'CONSUL_LOCAL_CONFIG={"skip_leave_on_interrupt": true}' \
-e 'CONSUL_HTTP_ADDR=$1:8500' consul agent -server \
-bind=$1 -bootstrap -ui -client=$1