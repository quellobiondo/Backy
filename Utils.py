#! /bin/usr/python

from weir import zfs

zpool_name = "zpool-docker"


def dataset_name(service):
    return "%s/%s" % (zpool_name, service)


def init_dataset(service, service_type):
    """
    Create the dataset for the service if it is of type
    production and the dataset doesn't exist
    """
    if service_type == "backup":
        return

    dataset = dataset_name(service)
    try:
        zfs.find(dataset, types=['filesystem'])
    except Exception:
        zfs.create(dataset)


def synchronize_snapshots(local_snaps, remote_snaps, server_name):
    """
    Synchronize all the snapshots metadata to the remote machine
    """
    for rem in remote_snaps:
        if local_snaps.get(rem, None):
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
    """
    Return the name of the latest snapshot in a list of snapshots
    """
    latest = None
    for sn in snaps:
        if latest is None or int(snaps[latest]["date"]) < int(snaps[sn]["date"]):
            latest = sn

    return latest
