# dockercylc

The alpine version is just an alpine container with cylc installed.  
The gui version provides an easy and fast way to get your cylc app up and running with a gui.
https://cloud.docker.com/swarm/alexanderpaulsell/repository/docker/alexanderpaulsell/cylc

## Environment Variables

| Environment variable | Description |
| ----------------------- | ----------------------------------------------------------------------------- |
| suitename | On runtime the container will register /dockercylc/${suitename} and run cylc gui for it |
| coldstart | If set to 1 will coldstart suite on runtime |
| warmstart | If set to 1 will warmstart suite on runtime |
| startpoint| Startpoint if warmstarting suite |
| restart   | If set to 1 will restart suite on runtime. This requires a volume mount to /dockercylc/cylc-run/ |

## Prerequisites

Enable shared drives in docker settings.


## Quick Start

docker build -t cylc PathToDockerfile

docker run -it -v PATH:/dockercylc/suitename -p 5800:5800 cylc

Where PATH is the absolute path to the folder containing a suite.rc file

Go to localhost:5800 on any web browser. You'll see a cylc gui. Run the suite.


## Packages

The simplest way to get specific packages for your suite is to make a new image, inherit alexanderpaulsell/cylc, then install packages.
pip is already installed otherwise use alpines package manager.  

###### Example

FROM alexanderpaulsell/cylc  
RUN pip install BeautifulSoup


## Notes

A different volume can be in your suite definition volume: -v PATH_TO_SUITE_DEF:/dockercylc/suitename/ -v PATH_TO_SOMEWHERE_ELSE:/dockercylc/suitename/data/

This may create empty folders in PATH_TO_SUITE_DEF

Setting a volume to cylc-run is dangerous; if the container is shut down unexpectedly without first stopping the suite you cannot restart the suite.

Because the container is linux, if your files were writen in dos you may need to run dos2unix.  

## Credit

Credit to jlesage for making the suite gui easily visible.

https://github.com/jlesage/docker-baseimage-gui
