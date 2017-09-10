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

service docker start

apt-get install python3-pip

echo "Intalling Sanoid"
apt-get install -y libconfig-inifiles-perl git lzop mbuffer
cd /opt
git clone https://github.com/jimsalterjrs/sanoid
ln /opt/sanoid/sanoid /usr/sbin/
ln /opt/sanoid/syncoid /usr/sbin/

mkdir -p /etc/sanoid
cp /opt/sanoid/sanoid*.conf /etc/sanoid/

echo "Activating consul client"
docker run -d --net=host -e 'CONSUL_LOCAL_CONFIG={"leave_on_terminate": true}' \
--name consul_client consul agent -bind=$1 \
-retry-join=$2