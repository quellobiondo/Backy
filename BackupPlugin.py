#! /bin/usr/python

from random import shuffle

import consul

from KVwrapper import retrieve_remote_snapshot_metadata, update_remote_metadata, get_server_list, get_node_meta
from Utils import dataset_name, get_latest_snapshot
from plugin.SanoidBackupPlugin import SanoidBackupPlugin

"""
Generic backup plugin
- Allow to apply backup policy
- Define entry point for backup
- Uses Key-Value store to take snapshots
"""


class BackupPlugin(object):
    def __init__(self, kv, node, snapshot_driver):
        self.kv = kv
        self.driver = snapshot_driver
        self.node = node

    def get_remote_snapshots(self, service):
        """
        Return all the snapshots from the kv-store
        """
        return retrieve_remote_snapshot_metadata(self.kv, service)

    def take_snapshot(self, service, name=None):
        """
        Take a snapshot and update kv-store metadata
        """

        self.driver.take_snapshot(dataset_name(service), name)
        update_remote_metadata(self.kv, self.node, service, self.get_snapshots(service))

    def store_backup_policy(self, service_name, service_type, policy):
        """
        Apply to the driver required policy
        """
        self.driver.apply_backup_policy(service_name, policy[service_type])

    def get_snapshots(self, service):
        """
        Return local snapshots for the given service using underlying plugin
        """
        try:
            return self.driver.get_snapshots(service)
        except Exception:
            return {}

    def pull_recent_snapshots(self, service):
        """
        Retrieve latest snapshot from remote for the given service.
        If is different than the last saved inside this container
        Pull snapshots from one of the machines
        """
        local_snapshosts = self.get_snapshots(service)
        remote_snapshots = retrieve_remote_snapshot_metadata(self.kv, service)
        local_latest_snap = get_latest_snapshot(local_snapshosts)
        remote_latest_snap = get_latest_snapshot(remote_snapshots)

        print("Pulling snaps ? %s %s" % (local_latest_snap, remote_latest_snap))
        if not remote_latest_snap:
            return False

        if not local_latest_snap or \
                        local_snapshosts[local_latest_snap]["date"] < remote_snapshots[remote_latest_snap]["date"]:

            server_list = get_server_list(self.kv, service, remote_latest_snap)
            # randomize list
            shuffle(server_list)
            print("From who? %s " % server_list)
            for server in server_list:
                server_meta = get_node_meta(self.kv, server)
                server_addr = server_meta["address"]
                self.driver.pull(server_addr, service)
                # assuming always success
                update_remote_metadata(self.kv, self.node, service, local_snapshosts)
                return True

        return False

    @staticmethod
    def factory(plugin_type):
        """
        Return a Backup object with its driver (Sanoid/Syncoid)
        a kv-store (Consul) and meta-data for the node in which
        this service is execute (retrieved by consul)
        """

        driver = SanoidBackupPlugin("/opt/sanoid/sanoid", "/opt/sanoid/syncoid")
        cons = consul.Consul()

        node = {
            "Name": cons.agent.self()["Member"]["Name"],
            "Address": cons.agent.self()["Member"]["Addr"],
            "Type": plugin_type
        }
        return BackupPlugin(cons.kv, node, driver)
