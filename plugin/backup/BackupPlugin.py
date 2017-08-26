#! /bin/usr/python

import os

import consul
from .SanoidBackupPlugin import SanoidBackupPlugin
from .MockBackupPlugin import MockBackupPlugin, MockKeyValueStore

"""
Generic backup plugin
- Allow to apply backup policy
- Define entry point for backup
- Uses Key-Value store to take snapshots
"""


class BackupPlugin(object):
    def __init__(self, kv, snapshot_driver):
        self.kv = kv
        self.driver = snapshot_driver

    def take_snapshot(self):
        self.driver.take_snapshot()
        self.kv.put('snapshot', self.get_snapshot())

    def apply_backup_policy(self, policy):
        pass

    def get_snapshot(self):
        pass

    @staticmethod
    def factory():
        driver = SanoidBackupPlugin("/opt/sanoid/sanoid")
        kv = consul.Consul().kv

        # driver = MockBackupPlugin()
        # kv = MockKeyValueStore()

        return BackupPlugin(kv, driver)


if __name__ == "__main__":
    backup = BackupPlugin.factory()

