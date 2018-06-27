# use official Python runtime as parent image
FROM jlesage/baseimage-gui:alpine-3.7-glibc

ENV suitename=helloworld
ENV APP_NAME="dockercylc"

# set working dir to /dockercylc
WORKDIR /dockercylc

# install cylc and ready suite
RUN add-pkg xterm curl python py-pip py-openssl py-requests py-gtk py-graphviz openssl make bash ; \
	cd /opt && curl -# -L https://github.com/cylc/cylc/archive/7.7.0.tar.gz | tar -xz ; \
	cp /opt/cylc-7.7.0/usr/bin/cylc /usr/local/bin/ ; \
	cd /opt/cylc-7.7.0/ && make ; \
	ln -s /opt/cylc-7.7.0/ /opt/cylc ; \
	mkdir /dockercylc/cylc-run ; \
	printf "[hosts]\n" > /opt/cylc-7.7.0/etc/global.rc ; \ 
	printf "[[localhost]]\n" >> /opt/cylc-7.7.0/etc/global.rc ; \
	printf "run directory = /dockercylc/cylc-run\n" >> /opt/cylc-7.7.0/etc/global.rc ; \
	printf "work directory = /dockercylc/cylc-run" >> /opt/cylc-7.7.0/etc/global.rc ; \
	chmod -R 777 /dockercylc/cylc-run

# x gui
RUN \
	printf "#!/bin/sh\n" > /startapp.sh ; \
	printf "export HOME=/dockercylc/\n" >> /startapp.sh ; \
	printf "cp /dockercylc/\$suitename/suite.rc /dockercylc/cylc-run/\$suitename/\n" >> /startapp.sh ; \
	printf "exec cylc gui \$suitename\n" >> /startapp.sh

# make port 8000 available to the world outside container
EXPOSE 8000