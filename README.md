# dockercylc

| Environment variable | Description |

| -------------------- | -----------------------------------------------------------------------------|

| suitename | On runtime the container will register /dockercylc/${suitename} and run cylc gui for it |
  
| coldstart | If set to 1 will coldstart suite on runtime |
  
| warmstart | If set to 1 will warmstart suite on runtime |
  
| startpoint| Startpoint if warmstarting suite |
  
| restart   | If set to 1 will restart suite on runtime. This requires a volume mount to /dockercylc/cylc-run/ |

Prerequisites:
Enable shared drives in docker settings.

Basic start:
docker build -t cylc PathToDockerfile
docker run -it -v ABSOLUTE_PATH_TO_SUITE_FOLDER:/dockercylc/suitename -p 5800:5800 cylc
Go to localhost:5800 on any web browser. You'll see a cylc gui. Run the suite.

Notes:
A different volume can be in your suite definition volume: -v PATH_TO_SUITE_DEF:/dockercylc/suitename/ -v PATH_TO_SOMEWHERE_ELSE:/dockercylc/suitename/data/
This may create empty folders in PATH_TO_SUITE_DEF
Setting a volume to cylc-run is dangerous; if the container is shut down unexpectedly without first stopping the suite you cannot restart the suite.
