#! /bin/usr/python

import json

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
        self.node = {
            "Name": cons.agent.self()["Member"]["Name"],
            "Address": cons.agent.self()["Member"]["Addr"]
        }

    def load_config(self):
        return {
            "zpool-docker/myapp":
                {
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
        }

    def syncronize_snapshots(self, local_snaps, remote_snaps, server_name):
        for rem in remote_snaps:
            for local in local_snaps:
                if local[rem.tag]:
                    # Esiste in locale lo snapshot con il tag rem.tag
                    if server_name not in rem.server:
                        rem.server.append(server_name)
                else:
                    # Non esiste più lo snapshot
                    if server_name in rem.server:
                        rem.server.remove(server_name)

        for new_snap in [x for x in local_snaps.keys() if x not in remote_snaps.keys()]:
            remote_snaps[new_snap] = local_snaps[new_snap]
            remote_snaps[new_snap]["server"] = [server_name]
        return remote_snaps

    def get_latest_snapshot(self, snaps):
        latest = None
        for sn in snaps:
            if latest is None or int(latest.date) < int(sn.date):
                latest = sn
        return latest

    def retrieve_remote_snapshot_metadata(self):
        index, value = self.kv.get('snapshots/myapp')
        if not value:
            value = {"Value": ""}

        all_snapshots = value["Value"]
        if all_snapshots:
            # stringa vuota
            all_snapshots = json.loads(all_snapshots.decode('utf-8'))
        else:
            all_snapshots = {}
        return all_snapshots

    def take_snapshot(self, dataset=None, name=None):
        self.driver.take_snapshot(dataset, name)

        all_snapshots = self.retrieve_remote_snapshot_metadata()
        local_snapshots = self.driver.get_snapshots()
        sync_result = self.syncronize_snapshots(local_snapshots, all_snapshots, self.node["Name"])
        self.kv.put('snapshots/myapp', json.dumps(sync_result))

        latest_snap = self.get_latest_snapshot(sync_result)
        self.kv.put('services/myapp', latest_snap.tag)
        self.kv.put('nodes/%s' % (self.node("Name")),
                    {
                        "type": "production",
                        "backups": json.dump(local_snapshots)
                    })

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

