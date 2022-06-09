## <a name='TheprocessofadaptingPythonCallingDocker'></a>The process of adapting PythonCallingDocker

### <a name='CreationofArgoWorkflowsDockerCollect-DockerContext'></a>Creation of ArgoWorkflows/Docker/Collect-DockerContext

Oddly enough the PythonCallingDocker version of the pipeline does not use the
container defined by LyonTemporal/Docker/Collect-DockerContext/. Instead it
choses to re-implement, in Python, the downloading process. The reason for
doing so was to be able to extend the downloading process feature with the
application of patches as well as being able to handle the directory tree
that this Python based version of the pipeline is able to propagate (or deal
with) along the different stages of the pipeline.
