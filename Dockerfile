#
# Production Backup as a Service based on ZFS Dockerfile
#
# https://github.com/quellobiondo/Backy
#

# Pull base image.
FROM ubuntu:16.04

# Install ZFS
RUN apt-get update && apt-get install -y zfsutils-linux

# Install Sanoid, git, Python
RUN apt-get install -y \
	git \
	libconfig-inifiles-perl \
	init \
	lzop \
	mbuffer \
	python \
	python-pip \
	python-dev \
	build-essential \
	cron

# Define working directory.
WORKDIR /opt/

RUN git clone https://github.com/jimsalterjrs/sanoid

WORKDIR /opt/sanoid/

RUN mkdir -p /etc/sanoid && cp sanoid*.conf /etc/sanoid/

RUN pip install --upgrade pip

COPY . .

RUN pip install -r requirements.txt

# Define default command.
ENTRYPOINT ["python", "configure.py"]

CMD ["production"]