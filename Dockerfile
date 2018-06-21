# use official Python runtime as parent image
FROM jlesage/baseimage-gui:alpine-3.7-glibc

# set working dir to /cylctest
WORKDIR /cylctest

# x gui
COPY startapp.sh /startapp.sh
RUN dos2unix /startapp.sh

# cylc
RUN mkdir helloworld
RUN mkdir -p /opt /cylctest/cylc-run/helloworld
ADD ./helloworld /cylctest/helloworld
ADD ./helloworld/suite.rc /cylc-run/helloworld

# web based cylc
RUN mkdir WebBasedCylc/
ADD ./WebBasedCylc/ /cylctest/WebBasedCylc

# packages needed
RUN add-pkg xterm curl ; \
	apk add --update python py-pip py-openssl py-requests py-gtk py-graphviz openssl make bash ; \
	pip install -r WebBasedCylc/requirements.txt ; \
	rm -rf /var/cache/apk/*

# install cylc and ready suite
RUN cd /opt && curl -# -L https://github.com/cylc/cylc/archive/7.7.0.tar.gz | tar -xz 
RUN cp /opt/cylc-7.7.0/usr/bin/cylc /usr/local/bin/
RUN	cd /opt/cylc-7.7.0/ && make
RUN	ln -s /opt/cylc-7.7.0/ /opt/cylc
RUN cylc register helloworld ./helloworld/ && cp /cylctest/helloworld/suite.rc /cylctest/cylc-run/helloworld/

RUN \
	printf "[hosts]\n" > /opt/cylc-7.7.0/etc/global.rc ; \ 
	printf "[[localhost]]\n" >> /opt/cylc-7.7.0/etc/global.rc ; \
	printf "run directory = /cylctest/cylc-run\n" >> /opt/cylc-7.7.0/etc/global.rc ; \
	printf "work directory = /cylctest/cylc-run" >> /opt/cylc-7.7.0/etc/global.rc

RUN chmod -R 777 /cylctest

# make port 8000 available to the world outside container
EXPOSE 8000

# define environment variable
ENV APP_NAME="cylctest"
#ENV USER_ID=0
#ENV GROUP_ID=0

# run app.py when the container launches
#CMD ["cylc","run","basic"]
#CMD ["ls"]
#CMD python ./WebBasedCylc/manage.py runserver
#ENTRYPOINT ["python","./WebBasedCylc/manage.py"]
#CMD ["runserver", "0.0.0.0:8000"]