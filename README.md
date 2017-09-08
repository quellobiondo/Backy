# Backy
Distributed backup system for containerized systems.

# Usage 
Backy container has to execute as --privileged (because of ZFS).

### CONSUL

execute server
docker run -d --name consul-server --net=host -e 'CONSUL_LOCAL_CONFIG={"skip_leave_on_interrupt": true}' -e 'CONSUL_HTTP_ADDR=192.168.33.105:8500' consul agent -server -bind=192.168.33.105 -bootstrap -ui -client=192.168.33.105

execute client
docker run -d --net=host -e 'CONSUL_LOCAL_CONFIG={"leave_on_terminate": true}' --name consul_client consul agent -bind=192.168.33.102 -retry-join=192.168.33.105

Service autodiscovery -- registrator
```
docker run -d \
    --name=registrator \
    --net=host \
    --volume=/var/run/docker.sock:/tmp/docker.sock \
    gliderlabs/registrator:latest \
      consul://localhost:8500
```
### Backy

```
docker build -t backy-service .
docker run -d -it --name backy --net=host --privileged backy-service production zpool-docker/myapp
docker exec -it backy /bin/bash
```
