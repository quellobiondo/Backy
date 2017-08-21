# Backy
Distributed backup system for containerized systems.

#### Usage
- TYPE: production or backup
- BACKUPS: "number of hourly backups, n° of daily backups, n° of monthly backups, n° of yearly backups"
- DATASET: "the ZFS dataset to use"

`docker run -it --env DATASET=tank/myapp --env TYPE=production --env BACKUPS="10, 5, 2, 1" --name backy-service --privileged ziro/backy:first`
