#! /bin/usr/python

# from .BackupPlugin import BackupPlugin

import json

from weir import zfs

"""
Backup plugin based on Sanoid, tool for ZFS
"""

from subprocess import call


class SanoidBackupPlugin(object):
    def __init__(self, binary):
        self.binary = binary

    def take_snapshot(self, dataset=None, name=None):
        if dataset and name:
            print("Taking snapshot as requested")
            call(["zfs", "snapshot", "%s@%s" % (dataset, name)])
            return True
        else:
            print("Activating policy daemon")
            # Rispetta le politiche
            call([self.binary])

    def apply_backup_policy(self, policy):
        with open('/etc/backy/backy.conf', 'w') as out:
            json.dump(policy, out)

        with open('/etc/sanoid/sanoid.conf', 'w') as out:
            out.write("""
        [{dataset}]
            use_template = production
            recursive = yes

            hourly = {n_hour}
            daily = {n_day}
            monthly = {n_month}
            yearly = {n_year}
            autosnap = {take}
            autoprune = {prune}

        [template_production]
        	hourly = 36
        	daily = 30
        	monthly = 3
        	yearly = 0
        	autosnap = yes
        	autoprune = yes
        	""".format(**policy))

    def get_snapshots(self):
        datasets = ["zpool-docker/myapp"]

        snaps = {}
        for dataset in datasets:
            for snap in zfs.open(dataset).snapshots():
                snaps[snap.name] = {
                    "date": snap.getprop("creation")["value"]
                }
        return snaps
