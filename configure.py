#! /bin/python

"""
Backy: Backup as a service based on ZFS for containerized applications.
"""

import argparse
import logging
import sys

import os
from crontab import CronTab

from plugin.backup.BackupPlugin import BackupPlugin


def setup(number_of_backups, type):
    configuration = {'take': "yes", 'prune': "yes",
                     'n_hour': number_of_backups[0], 'n_day': number_of_backups[1],
                     'n_month': number_of_backups[2], 'n_year': number_of_backups[3]}

    if type == "production":
        configuration['take'] = "yes"
        configuration['prune'] = "yes"
    elif type == "backup":
        configuration['take'] = "no"
        configuration['prune'] = "yes"

    print("Conf: %s" % configuration)
    return configuration


def activate_cron_job(binary):
    logging.debug("Activating automatic backup")

    backup_job = CronTab(user='root')
    job = backup_job.new(command="/usr/bin/python3 " + binary)
    job.minute.every(1)
    backup_job.write()

    logging.debug(backup_job)


def configure(args):
    settings = setup(args.backups.split(' '), args.type)

    BackupPlugin.factory(args.type).store_backup_policy(args.service, settings)

    binary_path = os.path.abspath(os.path.dirname(sys.argv[0])) + "/" + sys.argv[0]
    binary_args = "%s %s %s" % ("cron", args.type, args.service)

    print("CronJob: %s %s" % (binary_path, binary_args))
    activate_cron_job("%s %s" % (binary_path, binary_args))

    print("Press ENTER to end")
    input()


def do_cron_job(args):
    if args.type == "production":
        BackupPlugin.factory(args.type).take_snapshot(args.service, "")
    else:
        BackupPlugin.factory(args.type).pull_recent_snapshots(args.service)


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
    parser_configure.add_argument("--backups", type=check_backups_args, default="10 5 2 0")
    parser_configure.add_argument("service", type=check_service)

    parser_cron = subparsers.add_parser('cron')
    parser_cron.add_argument("type", choices=['production', 'backup'])
    parser_cron.add_argument("service", type=check_service)

    args = parser.parse_args()

    if args.possibilita == "cron":
        do_cron_job(args)
    elif args.possibilita == "configure":
        configure(args)
