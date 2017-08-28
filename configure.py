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

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def setup(number_of_backups, type, services):
    configuration = {'dataset': "--", 'take': "yes", 'prune': "yes",
                     'n_hour': number_of_backups[0], 'n_day': number_of_backups[1],
                     'n_month': number_of_backups[2], 'n_year': number_of_backups[3]}

    if type == "production":
        configuration['take'] = "yes"
        configuration['prune'] = "yes"
    elif type == "backup":
        configuration['take'] = "no"
        configuration['prune'] = "yes"

    configuration['dataset'] = services

    logging.debug(configuration)
    return configuration


def activate_backups(binary):
    logging.debug("Activating automatic backup")

    backup_job = CronTab(user='root')
    job = backup_job.new(command="/usr/bin/python3 " + binary)
    job.minute.every(1)
    backup_job.write()

    logging.debug(backup_job)


def configure(args):
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.debug(args)
    settings = setup(args.backups.split(' '), args.type, args.dataset)

    BackupPlugin.factory().apply_backup_policy(settings)

    activate_backups(os.path.abspath(os.path.dirname(sys.argv[0])) + "/" + sys.argv[0] + " snapshot")
    print("Press ENTER to end")
    input()


def take_snapshot(args):
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    logger.debug("Take backup")
    BackupPlugin.factory().take_snapshot(args.name, args.dataset)

def check_backups_args(string):
    return string

def check_dataset(string):
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
    parser_configure.add_argument("dataset", type=check_dataset)

    parser_snapshot = subparsers.add_parser('snapshot')
    parser_snapshot.add_argument("--name", default="")
    parser_snapshot.add_argument("--dataset", type=check_dataset, default="")

    args = parser.parse_args()

    if args.possibilita == "snapshot":
        take_snapshot(args)
    elif args.possibilita == "configure":
        configure(args)