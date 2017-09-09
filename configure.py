#! /bin/python

"""
Backy: Backup as a service based on ZFS for containerized applications.
"""

import argparse
import logging
import sys

import os
from crontab import CronTab

import KVwrapper
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
        "weekly": values[2],
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

    backup.store_backup_policy(service_name, policy)


def configure(arguments):
    service_name = arguments.service
    service_type = arguments.type

    backup = BackupPlugin.factory(service_type)
    configure_policy(backup, backup.kv, service_name, service_type)

    activate_cron_job(service_type, service_name)

    print("Press ENTER to end")
    input()


def activate_cron_job(service_type, service_name):
    logging.debug("Activating automatic backup")
    binary_path = os.path.abspath(os.path.dirname(sys.argv[0])) + "/" + sys.argv[0]
    binary_args = "%s %s %s" % ("cron", service_type, service_name)

    print("CronJob: %s %s" % (binary_path, binary_args))
    binary = "%s %s" % (binary_path, binary_args)

    backup_job = CronTab(user="root")
    job = backup_job.new(command="/usr/bin/python3 " + binary)
    job.minute.every(1)
    backup_job.write()

    logging.debug(backup_job)


def do_cron_job(arguments):
    if arguments.type == "production":
        BackupPlugin.factory(arguments.type).take_snapshot(arguments.service, "")
    else:
        BackupPlugin.factory(arguments.type).pull_recent_snapshots(arguments.service)


def check_backups_args(string):
    return string


def check_service(string):
    return string


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
    parser_configure.add_argument("-pp", "--policy_production", type=check_backups_args, default=None)
    parser_configure.add_argument("-pb", "--policy_backup", type=check_backups_args, default=None)
    parser_configure.add_argument("service", type=check_service)

    parser_cron = subparsers.add_parser('cron')
    parser_cron.add_argument("type", choices=['production', 'backup'])
    parser_cron.add_argument("service", type=check_service)

    args = parser.parse_args()

    if args.possibilita == "cron":
        do_cron_job(args)
    elif args.possibilita == "configure":
        configure(args)
