#! /usr/bin/python

import json

from Utils import synchronize_snapshots, get_latest_snapshot


def service_key(service):
    return 'services/%s' % service


def snapshot_key(service):
    return "%s/snapshots" % service_key(service)


def policy_key(service):
    return '%s/policy' % service_key(service)


def node_key(node_name):
    return 'nodes/%s' % node_name


def get_node_meta(kv, node):
    """
    Get metadata for the given node from key-value store
    """
    index, value = kv.get(node_key(node))
    if not value:
        value = {"Value": ""}

    meta = value["Value"]
    if meta:
        return json.loads(meta.decode('utf-8'))
    else:
        return {}


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
    # print("Snapshots %s" % snapshots)
    # tag = tag_from_snapshot(snapshot)
    return snapshots[snapshot].get("server", [])


def update_remote_metadata(kv, current_node, service, local_snapshots):
    """
    Update snapshots and node metadata on the key-value store
    """

    all_snapshots = retrieve_remote_snapshot_metadata(kv, service)
    sync_result = synchronize_snapshots(local_snapshots, all_snapshots, current_node["Name"])
    kv.put(snapshot_key(service), json.dumps(sync_result))

    latest_snap = get_latest_snapshot(sync_result)

    kv.put(service_key(service),
           json.dumps(
               {
                   "latest": latest_snap
               }
           )
           )

    kv.put(node_key(current_node["Name"]),
           json.dumps(
               {
                   "type": current_node["Type"],
                   "address": current_node["Address"],
                   "backups": local_snapshots
               })
           )


def store_backup_policy(kv, service_name, policy):
    """
    Save the policy for the given service on the Key-Value store
    """
    kv.put(policy_key(service_name), json.dumps(policy))


def get_backup_policy(kv, service):
    """
    Return the actual policy for that service registered on the key-value store
    """
    index, value = kv.get(policy_key(service))
    return json.loads(value["Value"].decode('utf-8'))
