#! /usr/bin/python

import datetime

class MockBackupPlugin(object):

    snapshots = []

    def __init__(self):
        self.snapshots.append({
            'name': "This is a Mock snapshot -- preconfigured",
            'date': datetime.datetime.now().time(),
            'dataset': "my_mock_dataset"
        })

    def take_snapshot(self):
        print("This is a Mock snapshot -- taken")
        self.snapshots.append({
                'name': "This is a Mock snapshot -- taken",
                'date': datetime.datetime.now().time(),
                'dataset': "my_mock_dataset"
        })

    def apply_backup_policy(self, policy):
        self.policy = policy

    def get_snapshots(self):
        return self.snapshots

class MockKeyValueStore():
    keyvalue = {}

    def put(self, key, value):
        self.keyvalue[key] = value

    def get(self, key):
        return self.keyvalue[key]