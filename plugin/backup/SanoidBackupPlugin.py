#! /bin/usr/python

# from .BackupPlugin import BackupPlugin

"""
Backup plugin based on Sanoid, tool for ZFS
"""

from subprocess import call

class SanoidBackupPlugin(object):

    def __init__(self, binary):
        self.binary = binary

    def take_snapshot(self):
        call([self.binary])

    def apply_backup_policy(self, policy):
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
        return "Mock-snapshot"
