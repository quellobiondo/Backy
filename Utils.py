#! /bin/usr/python

from weir import zfs

zpool_name = "docker-zpool"


def dataset_name(service):
    return "%s/%s" % (zpool_name, service)


def init_dataset(service):
    """
    Create the dataset for the service if not exists
    """
    dataset = dataset_name(service)
    if len(zfs.find(service, max_depth=1, types=['filesystem'])) == 0:
        zfs.create(dataset)


def tag_from_snapshot(snapshot):
    return snapshot.split('@', 1)[1]


def synchronize_snapshots(local_snaps, remote_snaps, server_name):
    """
    Synchronize all the snapshots metadata to the remote machine
    - removing the snapshots
    """
    for rem in remote_snaps:
        if local_snaps[rem]:
            # Esiste in locale lo snapshot con il tag rem.tag
            if server_name not in remote_snaps[rem]["server"]:
                remote_snaps[rem]["server"].append(server_name)
        else:
            # Non esiste più lo snapshot
            if server_name in remote_snaps[rem]["server"]:
                remote_snaps[rem]["server"].remove(server_name)

    for new_snap in [x for x in local_snaps.keys() if x not in remote_snaps.keys()]:
        remote_snaps[new_snap] = local_snaps[new_snap]
        remote_snaps[new_snap]["server"] = [server_name]

    return remote_snaps


def get_latest_snapshot(snaps):
    latest = None
    for sn in snaps:
        if latest is None or int(snaps[latest]["date"]) < int(snaps[sn]["date"]):
            latest = sn
    return latest
