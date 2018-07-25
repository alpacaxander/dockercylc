FROM alpine

WORKDIR /dockercylc

RUN apk add curl python py-pip py-openssl py-requests py-gtk py-graphviz openssl make bash ; \
	mkdir /opt ; \
	cd /opt && curl -# -L https://github.com/cylc/cylc/archive/7.7.0.tar.gz | tar -xz ; \
	cp /opt/cylc-7.7.0/usr/bin/cylc /usr/local/bin/ ; \
	cd /opt/cylc-7.7.0/ && make ; \
	ln -s /opt/cylc-7.7.0/ /opt/cylc ; \
	mkdir /dockercylc/cylc-run ; \
	chmod -R 777 /dockercylc/cylc-run