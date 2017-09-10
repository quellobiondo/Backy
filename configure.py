#! /bin/python

"""
Backy: Backup as a service based on ZFS for containerized applications.
"""

import argparse
import sys
import time

import os
import schedule

import KVwrapper
import Utils
from BackupPlugin import BackupPlugin


def parse_policy(from_args, environ_key):
    """
    Load Policy configuration from environment variables and
    command line variables.
    Priority on command line variables
    """
    if not from_args and not os.environ.get(environ_key):
        raise ValueError("Backup policy is not set in both arguments and Environment")

    if from_args:
        values = [int(i) for i in from_args.split(" ")]
    else:
        values = [int(i) for i in os.environ.get(environ_key).split(" ")]

    if len(values) != 4:
        raise ValueError("Not all backups frequencies are specified! Format: hourly daily monthly yearly")

    policy = {
        "hourly": values[0],
        "daily": values[1],
        "monthly": values[2],
        "yearly": values[3]
    }
    return policy


def configure_policy(backup, kv, service_name, service_type):
    if service_type == "production":
        environ_key_policy_production = "PRODUCTION_POLICY"
        environ_key_policy_backup = "BACKUP_POLICY"

        policy = {"production": parse_policy(args.policy_production, environ_key_policy_production),
                  "backup": parse_policy(args.policy_backup, environ_key_policy_backup)}

        KVwrapper.store_backup_policy(kv, service_name, policy)
    else:
        policy = KVwrapper.get_backup_policy(kv, service_name)

    backup.store_backup_policy(service_name, service_type, policy)


def configure(arguments):
    service_name = arguments.service
    service_type = arguments.type

    Utils.init_dataset(service_name)

    backup = BackupPlugin.factory(service_type)
    configure_policy(backup, backup.kv, service_name, service_type)

    activate_cron_job(backup, service_type, service_name)

    while True:
        schedule.run_pending()
        time.sleep(1)


def activate_cron_job(backup, service_type, service_name):
    def job():
        print("Doing cron job...")
        if service_type == "production":
            print("Taking snapshots...")
            backup.take_snapshot(service_name, "")
        else:
            print("Pulling recent snapshots...")
            backup.pull_recent_snapshots(service_name)

    schedule.every(1).minutes.do(job)
    job()


if __name__ == "__main__":
    """
    Parse argument, load settings, apply to node
    """
    parser = argparse.ArgumentParser(sys.argv)
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")

    subparsers = parser.add_subparsers(help='sub-commands help', dest="possibilita")

    parser_configure = subparsers.add_parser('configure')
    parser_configure.add_argument("type", choices=['production', 'backup'])
    parser_configure.add_argument("-pp", "--policy_production", default=None)
    parser_configure.add_argument("-pb", "--policy_backup", default=None)
    parser_configure.add_argument("service")

    args = parser.parse_args()

    if args.possibilita == "configure":
        try:
            configure(args)
        except ConnectionError:
            print("ConnectionRefusedError (Are consul client and server active and configured?)")
    else:
        parser.print_usage()
