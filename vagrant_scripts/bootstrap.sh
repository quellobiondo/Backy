#!/usr/bin/env bash

apt-get update

echo "Installing ZFS...\n"
apt-get install -y zfsutils-linux

echo "Creating volume "
VOLUME_PATH="/opt/zfsvolumes"
DISK_NAME="zfs_docker_disk"
echo "$VOLUME_PATH/$DISK_NAME ...\n"

mkdir -p $VOLUME_PATH
fallocate -l 2GB "$VOLUME_PATH/$DISK_NAME"

zpool create -f zpool-docker -m /zpool-docker "$VOLUME_PATH/$DISK_NAME"

# echo "Configuring Docker with ZFS...\n"
# service docker stop
# rm -rf /var/lib/docker/*

# echo '{ "storage-driver":"zfs" }' > /etc/docker/daemon.json

service docker start

echo "Intalling Sanoid"
apt-get install -y libconfig-inifiles-perl git lzop mbuffer
cd /opt
git clone https://github.com/jimsalterjrs/sanoid
ln /opt/sanoid/sanoid /usr/sbin/
ln /opt/sanoid/syncoid /usr/sbin/

mkdir -p /etc/sanoid
cp /opt/sanoid/sanoid*.conf /etc/sanoid/
