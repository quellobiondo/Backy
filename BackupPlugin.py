#! /bin/usr/python

import consul

from KVwrapper import retrieve_remote_snapshot_metadata, update_remote_metadata, get_server_list
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
        return retrieve_remote_snapshot_metadata(self.kv, service)

    def take_snapshot(self, service, name=None):
        self.driver.take_snapshot(dataset_name(service), name)
        update_remote_metadata(self.kv, self.node, service, self.get_snapshots(service))

    def store_backup_policy(self, service_name, service_type, policy):
        """
        Apply to the driver required policy
        Update remote server policy
        """
        self.driver.apply_backup_policy(service_name, policy[service_type])
        update_remote_metadata(self.kv, self.node, service_name, self.get_snapshots(service_name))

    def get_snapshots(self, service):
        return self.driver.get_snapshots(service)

    def pull_recent_snapshots(self, service):
        """
        Retrieve latest snapshot from remote for the given service.
        If is different than the last saved inside this container
        Pull snapshots from one of the machines
        """
        local_snapshosts = self.get_snapshots(service)

        local_latest_snap = get_latest_snapshot(local_snapshosts)
        remote_latest_snap = get_latest_snapshot(retrieve_remote_snapshot_metadata(self.kv, service))

        if remote_latest_snap and local_latest_snap \
                and local_latest_snap["date"] < remote_latest_snap["date"]:
            server_list = get_server_list(self.kv, service, remote_latest_snap)

            for server in server_list:
                self.driver.pull(server, service)
                # assuming always success
                update_remote_metadata(self.kv, self.node, service, local_snapshosts)
                return True

        return False

    @staticmethod
    def factory(plugin_type):
        driver = SanoidBackupPlugin("/opt/sanoid/sanoid", "/opt/sanoid/syncoid")
        cons = consul.Consul()

        node = {
            "Name": cons.agent.self()["Member"]["Name"],
            "Address": cons.agent.self()["Member"]["Addr"],
            "Type": plugin_type
        }
        return BackupPlugin(cons.kv, node, driver)