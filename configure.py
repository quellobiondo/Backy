#! /bin/python

"""
Backy: Backup as a service based on ZFS for containerized applications.
"""

import os
import sys
from crontab import CronTab

def setup():
	settings = {'dataset': "--", 'take': "yes", 'prune': "yes", "n_hour": 10, "n_day": 5, "n_month": 2, "n_year": 0}

	number_of_backups = []
	# mylist = [int(x) for x in os.getenv('BACKUPS', '10, 5, 2, 1').split(',')]
	[number_of_backups.append(int(x)) for x in os.getenv('BACKUPS', '10, 5, 2, 1').split(',')]
	settings['n_hour'] = number_of_backups[0]
	settings['n_day'] = number_of_backups[1]
	settings['n_month'] = number_of_backups[2]
	settings['n_year'] = number_of_backups[3]


	type = os.environ.get('TYPE')
	if type == "production":
		settings['take'] = "yes"
		settings['prune'] = "yes"
	elif type == "backup":
		settings['take'] = "no"
		settings['prune'] = "yes"
	else:
		sys.exit("Error: TYPE env not setted")

	settings['dataset'] = os.environ.get("DATASET")
	return settings

def createConfig(settings):
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
	""".format(**settings))

def launchCronJob():
	backup_job = CronTab(user='root')
	job = backup_job.new(command='/opt/sanoid/sanoid')
	job.minute.every(1)
	backup_job.write()
	#first launch
	os.system("/opt/sanoid/sanoid")


if __name__ == "__main__":
	settings = setup()
	createConfig(settings)
	launchCronJob()
