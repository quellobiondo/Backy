#! /bin/usr/python

from weir import zfs

from Utils import dataset_name

"""
Backup plugin based on Sanoid, tool for ZFS
"""

from subprocess import call


class SanoidBackupPlugin(object):
    def __init__(self, sanoid_binary, syncoid_binary):
        self.sanoid = sanoid_binary
        self.syncoid = syncoid_binary

    def take_snapshot(self, service, name=None):
        if name:
            print("Taking snapshot as requested")
            call(["zfs", "snapshot", "%s@%s" % (dataset_name(service), name)])
            return True
        else:
            print("Activating policy daemon")
            # Rispetta le politiche
            call([self.sanoid, "--cron"])
            return True

    @staticmethod
    def apply_backup_policy(service, policy):
        with open('/etc/sanoid/sanoid.conf', 'w') as out:
            out.write("""
        [{dataset}]
            use_template = production
            recursive = yes

            hourly = {p[hourly]}
            daily = {p[daily]}
            monthly = {p[monthly]}
            yearly = {p[yearly]}
            
        [template_production]
        	hourly = 36
        	daily = 30
        	monthly = 3
        	yearly = 0
        	autosnap = yes
        	autoprune = yes
        	""".format(dataset=dataset_name(service), p=policy))

    def pull(self, server, service):
        """
        Pull all missing snapshots from the remote server
        for the given service
        """
        server_data_set = "%s@%s:%s" % ("root", server, dataset_name(service))
        local_data_set = dataset_name(service)
        call([self.syncoid, server_data_set, local_data_set])

        return True

    @staticmethod
    def get_snapshots(service):
        datasets = [dataset_name(service)]

        snaps = {}
        for ds in datasets:
            for snap in zfs.open(ds).snapshots():
                snaps[snap.name] = {
                    "date": snap.getprop("creation")["value"]
                }
        return snaps