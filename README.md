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

`backy <type of service> <name of service>`

Backup policy decided as below.

type of service: "production" or "backup", production take snapshots, backup just replicate them

name of service: the name of the service that you want to backup, it will decide the name of the dataset

ex: myapp -> dataset="zpool-docker/myapp"


```
docker build -t backy-service .
docker run -d -it --rm --name backy -e PRODUCTION_POLICY="10 5 2 1" -e BACKUP_POLICY="15 5 2 2" --net=host --privileged backy-service production myapp
```
### Backup policy
How to setup backup policy (**ONLY** on boot of production container)

both policies have to be set on the boot-up of the production service

Precedence on command line arguments.
#### Command line arguments: 
    -pb or --policy-backup 
    -pp or --policy-production 

#### Environment variables: 
PRODUCTION_POLICY and BACKUP_POLICY

#### Values
"Hourly_backups   Daily_backups   Monthly_backups   Yearly_backups"

All values are integers, separated by spaces inside the same string

##### example 
`production -pp="10 5 2 1" -pb "10 5 2 1" myapp`

