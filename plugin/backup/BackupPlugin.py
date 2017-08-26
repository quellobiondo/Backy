#! /bin/usr/python

import json
from datetime import datetime

import consul

from .SanoidBackupPlugin import SanoidBackupPlugin

"""
Generic backup plugin
- Allow to apply backup policy
- Define entry point for backup
- Uses Key-Value store to take snapshots
"""


class BackupPlugin(object):
    def __init__(self, cons, snapshot_driver):
        self.kv = cons.kv
        self.driver = snapshot_driver
        self.node = cons.agent.self()["Member"]

    def load_config(self):
        return {
            "dataset": ["zpool-docker/myapp"]
        }

    def take_snapshot(self):
        self.driver.take_snapshot()

        dataset = self.load_config()["dataset"][0]

        index, value = self.kv.get('snapshots')

        # TODO: remove all the snapshots removed by this node
        all_snapshots = value["Value"]
        if not all_snapshots:
            # stringa vuota
            all_snapshots = json.load(all_snapshots)
        else:
            all_snapshots = []

        new_snapshot = {
            "dataset": dataset,
            "date": datetime.now().timestamp(),
            "nodo": self.node
        }

        all_snapshots.insert(0, new_snapshot)

        self.kv.put('snapshots', json.dumps(all_snapshots))

    def apply_backup_policy(self, policy):
        self.driver.apply_backup_policy(policy)

    def get_snapshots(self):
        return self.driver.get_snapshots()

    @staticmethod
    def factory():
        driver = SanoidBackupPlugin("/opt/sanoid/sanoid")
        cons = consul.Consul()

        return BackupPlugin(cons, driver)


if __name__ == "__main__":
    backup = BackupPlugin.factory()

