# Backy
Distributed backup system for containerized systems.

# Prerequisites

- Python3, python-pip3
- Root password-less SSH access to all machines
- Consul server running
- Consul client running on the same node
- ZPool zpool-docker on each machine
- Service's dataset not existing on all backup machines (syncoid prerequisite)

With the vagrant image everything is provided exept the root password-less login
between machines (you have to edit manually sshd conf and ssh-copy-id the keys for each machine)

# Usage 
Backy container has to execute as --privileged (because of ZFS).


### Backy

```
docker build -t backy-service .
docker run -d -it --name backy --net=host --privileged backy-service production zpool-docker/myapp
docker exec -it backy /bin/bash
```
