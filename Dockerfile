FROM jlesage/baseimage-gui:alpine-3.7-glibc

ENV suitename="suitename"
ENV APP_NAME="dockercylc"
ENV coldstart=0
ENV warmstart=0
ENV restart=0

WORKDIR /dockercylc

RUN add-pkg xterm curl python py-pip py-openssl py-requests py-gtk py-graphviz openssl make bash ; \
	cd /opt && curl -# -L https://github.com/cylc/cylc/archive/7.7.0.tar.gz | tar -xz ; \
	cp /opt/cylc-7.7.0/usr/bin/cylc /usr/local/bin/ ; \
	cd /opt/cylc-7.7.0/ && make ; \
	ln -s /opt/cylc-7.7.0/ /opt/cylc ; \
	mkdir /dockercylc/cylc-run ; \
	chmod -R 777 /dockercylc/cylc-run

RUN \
	printf "#!/bin/sh\n" > /startapp.sh ; \
	printf "export HOME=/dockercylc/\n" >> /startapp.sh ; \
	printf "cylc register \$suitename /dockercylc/\$suitename/\n" >> /startapp.sh ; \
	printf "if [ \$coldstart -eq 1 ]; then\n" >> /startapp.sh ; \
	printf "    cylc run \$suitename\n" >> /startapp.sh ; \
	printf "elif [ \$warmstart -eq 1 ]; then\n" >> /startapp.sh ; \
	printf "    cylc run --warm \$suitename \$startpoint\n" >> /startapp.sh ; \
	printf "elif [ \$restart -eq 1 ]; then\n" >> /startapp.sh ; \
	printf "    cylc restart \$suitename\n" >> /startapp.sh ; \
	printf "fi\n" >> /startapp.sh ; \
	printf "exec cylc gui \$suitename\n" >> /startapp.sh