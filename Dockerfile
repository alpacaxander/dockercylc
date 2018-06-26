# use official Python runtime as parent image
FROM jlesage/baseimage-gui:alpine-3.7-glibc

ARG suite=helloworld
ARG suitedir=.
ENV suitename=$suite
ENV coldstartsuite=0
ENV restartsuite=0
ENV APP_NAME="dockercylc"

# set working dir to /dockercylc
WORKDIR /dockercylc

# directorys
RUN mkdir -p /opt ./cylc-run/$suite

# packages needed
RUN add-pkg xterm curl \
	python py-pip py-openssl py-requests py-gtk py-graphviz openssl make bash

# x gui
RUN \
	printf "#!/bin/sh\n" > /startapp.sh ; \
	printf "export HOME=/dockercylc\n" >> /startapp.sh ; \
	printf "exec xterm\n" >> /startapp.sh ; \
	printf "if [ \$coldstartsuite -eq 1 ]; then\n" >> /startapp.sh ; \
	printf "    cylc run \$suitename\n" >> /startapp.sh ; \
	printf "elif [ \$restartsuite -eq 1 ]; then\n" >> /startapp.sh ; \
	printf "    cylc restart \$suitename\n" >> /startapp.sh ; \
	printf "fi\n" >> /startapp.sh ; \
	printf "exec cylc gui \$suitename\n" >> /startapp.sh

# install cylc and ready suite
RUN cd /opt && curl -# -L https://github.com/cylc/cylc/archive/7.7.0.tar.gz | tar -xz ; \
	cp /opt/cylc-7.7.0/usr/bin/cylc /usr/local/bin/ ; \
	cd /opt/cylc-7.7.0/ && make ; \
	ln -s /opt/cylc-7.7.0/ /opt/cylc
#	cd /dockercylc && cylc register $suite ./$suite/ # && cp ./$suite/suite.rc ./cylc-run/$suite/

RUN \
	printf "[hosts]\n" > /opt/cylc-7.7.0/etc/global.rc ; \ 
	printf "[[localhost]]\n" >> /opt/cylc-7.7.0/etc/global.rc ; \
	printf "run directory = /dockercylc/cylc-run\n" >> /opt/cylc-7.7.0/etc/global.rc ; \
	printf "work directory = /dockercylc/cylc-run" >> /opt/cylc-7.7.0/etc/global.rc

RUN chmod -R 777 /dockercylc/cylc-run

# make port 8000 available to the world outside container
EXPOSE 8000