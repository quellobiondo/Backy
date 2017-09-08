#! /usr/bin/python

import json

from .Utils import tag_from_snapshot, synchronize_snapshots, get_latest_snapshot


def snapshot_key(service):
    """
    :param service:
    :return: the name of the snapshots key for the service on the KV-store
    """
    return "snapshots/%s" % service


def service_key(service):
    """
    :param service:
    :return: the name of the service key on the KV-store
    """
    return 'services/%s' % service


def node_key(node_name):
    """
    :param node_name:
    :return: the name of the node key on the KV-store
    """
    return 'nodes/%s' % node_name


def retrieve_remote_snapshot_metadata(kv, service):
    """
    Get all snapshots for that service from key-value store
    """
    index, value = kv.get(snapshot_key(service))
    if not value:
        value = {"Value": ""}

    all_snapshots = value["Value"]
    if all_snapshots:
        all_snapshots = json.loads(all_snapshots.decode('utf-8'))
    else:
        all_snapshots = {}
    return all_snapshots


def get_server_list(kv, service, snapshot):
    """
    Return the servers that have that snapshot
    """
    snapshots = retrieve_remote_snapshot_metadata(kv, service)
    tag = tag_from_snapshot(snapshot)
    return snapshots[tag].get("server", [])


def update_remote_metadata(kv, current_node, service, local_snapshots, policy=None):
    """
    Update metadata on the key-value store
    """

    all_snapshots = retrieve_remote_snapshot_metadata(kv, service)
    sync_result = synchronize_snapshots(local_snapshots, all_snapshots, current_node["Name"])
    kv.put(snapshot_key(service), json.dumps(sync_result))

    latest_snap = get_latest_snapshot(sync_result)

    if policy is None:
        policy = get_backup_policy(kv, service)

    kv.put(service_key(service),
           json.dumps(
               {
                   "latest": latest_snap,
                   "policy": policy
               }
           )
           )

    kv.put(node_key(current_node["Name"]),
           json.dumps(
               {
                   "type": current_node["Type"],
                   "backups": local_snapshots
               })
           )


def get_backup_policy(kv, service):
    """
    Return the actual policy for that service registered on the key-value store
    or the default policy if it doesn't exist
    """
    default_policy = {
        "production": {
            "hourly": 10,
            "daily": 5,
            "weekly": 1,
            "yearly": 0,
            "frequency": 30
        },
        "backup": {
            "hourly": 10,
            "daily": 5,
            "weekly": 2,
            "yearly": 1
        }
    }

    index, value = kv.get(service_key(service))
    if value:
        return value["Value"].get("policy", default_policy)

    return default_policy
