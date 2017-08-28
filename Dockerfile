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
	python3 \
	python3-pip \
	python3-dev \
	build-essential \
	cron

# Define working directory.
WORKDIR /opt/

RUN git clone https://github.com/jimsalterjrs/sanoid

WORKDIR /opt/sanoid/

RUN mkdir -p /etc/sanoid && cp sanoid*.conf /etc/sanoid/

RUN pip3 install --upgrade pip

WORKDIR /opt/backy/

RUN mkdir -p /etc/backy

COPY . .

RUN pip3 install -r requirements.txt

# Define default command.
ENTRYPOINT ["python3", "configure.py", "configure"]

CMD ["production", "zpool-docker/myapp"]