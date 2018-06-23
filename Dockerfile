# use official Python runtime as parent image
FROM jlesage/baseimage-gui:alpine-3.7-glibc

ARG suite=helloworld
ARG suitedir=.

# set working dir to /dockercylc
WORKDIR /dockercylc

# packages needed
RUN add-pkg xterm curl \
	python py-pip py-openssl py-requests py-gtk py-graphviz openssl make bash ; \
	pip install -r WebBasedCylc/requirements.txt ; \
	rm -rf /var/cache/apk/*

# x gui
COPY startapp.sh /startapp.sh
RUN dos2unix /startapp.sh

# cylc
RUN mkdir -p $suite /opt ./cylc-run/$suite
ADD $suitedir ./$suite
ADD $suitedir/suite.rc ./cylc-run/$suite

# web based cylc
RUN mkdir WebBasedCylc/
ADD ./WebBasedCylc/ ./WebBasedCylc

# install cylc and ready suite
RUN cd /opt && curl -# -L https://github.com/cylc/cylc/archive/7.7.0.tar.gz | tar -xz ; \
	cp /opt/cylc-7.7.0/usr/bin/cylc /usr/local/bin/ ; \
	cd /opt/cylc-7.7.0/ && make ; \
	ln -s /opt/cylc-7.7.0/ /opt/cylc ; \
	cd /dockercylc && cylc register $suite ./$suite/ && cp ./$suite/suite.rc ./cylc-run/$suite/

RUN \
	printf "[hosts]\n" > /opt/cylc-7.7.0/etc/global.rc ; \ 
	printf "[[localhost]]\n" >> /opt/cylc-7.7.0/etc/global.rc ; \
	printf "run directory = /dockercylc/cylc-run\n" >> /opt/cylc-7.7.0/etc/global.rc ; \
	printf "work directory = /dockercylc/cylc-run" >> /opt/cylc-7.7.0/etc/global.rc

RUN chmod -R 777 /dockercylc/cylc-run

# make port 8000 available to the world outside container
EXPOSE 8000

# define environment variable
ENV APP_NAME="dockercylc"
#ENV USER_ID=0
#ENV GROUP_ID=0

# run app.py when the container launches
#CMD ["cylc","run","basic"]
#CMD ["ls"]
#CMD python ./WebBasedCylc/manage.py runserver
#ENTRYPOINT ["python","./WebBasedCylc/manage.py"]
#CMD ["runserver", "0.0.0.0:8000"]