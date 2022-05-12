<!-- vscode-markdown-toc -->
* [Preparation stage](#Preparationstage)
  * [Instal dependencies (infrastructure)](#Instaldependenciesinfrastructure)
  * [Expose the CWD as k8s volume](#ExposetheCWDask8svolume)
  * [Build the required containers](#Buildtherequiredcontainers)
  * [Populate the workflow "library" with workflowTemplates](#PopulatetheworkflowlibrarywithworkflowTemplates)
* [Running the workflows](#Runningtheworkflows)
  * [Running the workflow stage by stage: single vintage version](#Runningtheworkflowstagebystage:singlevintageversion)
  * [Running the workflow stage by stage: multiple vintages version](#Runningtheworkflowstagebystage:multiplevintagesversion)
  * [Running the full workflow](#Runningthefullworkflow)
  * [Running the full workflow](#Runningthefullworkflow-1)
* [Troubleshooting](#Troubleshooting)
  * [Hung up workflow (pending status)](#Hungupworkflowpendingstatus)
  * [Storage backend is full](#Storagebackendisfull)
  * [In case the minikube's k8s cluster gets corrupted](#Incasetheminikubesk8sclustergetscorrupted)
  * [Dealing with "using the emissary executor" error](#Dealingwithusingtheemissaryexecutorerror)
* [Developers](#Developers)
  * [Install utils](#Installutils)
  * [Running the examples](#Runningtheexamples)
  * [Running the ongoing issues/failures](#Runningtheongoingissuesfailures)
* [The process of adapting PythonCallingDocker](#TheprocessofadaptingPythonCallingDocker)
  * [Creation of ArgoWorkflows/Docker/Collect-DockerContext](#CreationofArgoWorkflowsDockerCollect-DockerContext)

<!-- vscode-markdown-toc-config
	numbering=false
	autoSave=true
	/vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->

# Running the implemented Argo workflows on a desktop with Minikube

## <a name='Preparationstage'></a>Preparation stage

### <a name='Instaldependenciesinfrastructure'></a>Instal dependencies (infrastructure)

The following was tested on `OSX 12.1` (Monterey) with `Homebrew 3.3.12`

Package install

```bash
brew install kubernetes-cli
kubectl version       # v1.23.2
alias k=kubectl
#
brew install minikube # 1.25.1
#
brew install argo     # 3.2.6
# or when the above fails with "no bottle is available" then use
#      brew install --build-from-source argo
```

Launching minikube

```bash
minikube --memory=8G --cpus 4 start
```

Notice that minikube announces that it downloads some version Kubernetes (e.g.
v1.20.2 preload)

```bash
k create ns argo     # Remember the k=kubectl shell alias (refer above)
export ARGO_NAMESPACE=argo
k config set-context --current --namespace=$ARGO_NAMESPACE
# Start an argo server
k apply -f https://raw.githubusercontent.com/argoproj/argo-workflows/master/manifests/quick-start-postgres.yaml
# and assert the AW controller is running with
k get pod | grep workflow-controller
```

If you wish to work with the UI, you need to open the ad-hoc port-forwarding
with the command

```bash
k -n argo port-forward deployment/argo-server 2746:2746 &
```

The web UI should be available at `https://localhost:2746`.

### <a name='ExposetheCWDask8svolume'></a>Expose the CWD as k8s volume

First expose the CWD (Current Working Directory) to minikube with

```bash
# Note the trailing ampersand of the following command
minikube mount `pwd`:/data/host &
```

The above command allows for the creation of a k8s
[`PersistentVolume` (PV)](https://kubernetes.io/docs/concepts/storage/persistent-volumes/):
refer to the usage of
[`/data/host` within `define_pvc_minikube.yaml`](define_pvc_minikube.yaml#L11).
And based on this PV, a  
[`PersistentVolumeClaim` (PVC)](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
can be defined:
refer to [this line within `define_pvc_minikube.yaml`](define_pvc_minikube.yaml#L16).

The creations of the PV and PVC can be done with

```bash
k -n argo create -f define_pvc_minikube.yaml
```

and assertion that all went well be done with

```bash
k -n argo get pvc | grep minikube-pvc
k -n argo create -f test_pvc_minikube.yaml 
```

Note: once the above `minikube mount` is issued a workflow could consume/access
it as a volume (refer to
[this example](https://minikube.sigs.k8s.io/docs/handbook/mount/))
with an entry (within an Argo WOrkflow) of the form

```bash
"volumes": [
  {
    "name": "host-mount",
    "hostPath": {
      "path": "/data/host"
    }
  }
]
```

Hence the `minikube mount` target argument (i.e. `/data/host`) has to be
aligned with the workflow volume definition.

### <a name='Buildtherequiredcontainers'></a>Build the required containers

<a name="anchor-build-containers"></a>

```bash
# User Minikube's built-in docker command, refer e.g. to
# https://stackoverflow.com/questions/42564058/how-to-use-local-docker-images-with-minikube
eval $(minikube docker-env)
docker build -t vcity/collect_lyon_data Docker/Collect-DockerContext/
docker build -t vcity/3duse ../Docker/3DUse-DockerContext/
docker build -t vcity/citygml2stripper ../Docker/CityGML2Stripper-DockerContext/
docker build --no-cache -t vcity/py3dtilers https://github.com/VCityTeam/py3dtilers-docker.git#:Context
docker pull refstudycentre/scratch-base:latest
```

Notes:

* In case of trouble with the docker builds (e.g. when the build failed
  because of missing disk space) consider using the `--no-cache` flag.

* `refstudycentre/scratch-base` is a really tiny container used as a trick
  (refer to workflow e.g. `Examples/loading-json-fromValue.yml`

* `docker build` can NOT use the url of sub-directory of git repository (refer
  e.g. to [this StackOverflow](https://stackoverflow.com/questions/25509828/can-a-docker-build-use-the-url-of-a-git-branch#27295336). This is why some
  of the above `docker build` commands designate their Dockerfile arguments
  through a relative path notation which creates an alas implicit dependency
  (within this repository).

### <a name='PopulatetheworkflowlibrarywithworkflowTemplates'></a>Populate the workflow "library" with workflowTemplates

<a name="anchor-populate-workflow-templates"></a>

[workflowTemplates](https://github.com/argoproj/argo-workflows/blob/release-3.2/docs/workflow-templates.md)
require a special treat and must be uploaded to the k8s cluster prior to using
(referring) them in a workflow.

```bash
# Remove ant preceding traces that could hinder the process 
\rm -fr junk     # Remove possible previous results to avoid collisions
argo template delete --all
# Add the template references
argo template create workflow-template/database.yml \
                     workflow-template/utils.yml \
                     workflow-template/atomic-steps.yml \
                     workflow-template/aggregated-templaterefs.yml
```

You can assert the `templateRef`s were properly created by e.g. listing them
with `argo template list`. Note: in case some cleanup is required then
the `argo template delete --all` merciless command might do the trick.

## <a name='Runningtheworkflows'></a>Running the workflows

### <a name='Runningtheworkflowstagebystage:singlevintageversion'></a>Running the workflow stage by stage: single vintage version

First make sure that the
[containers are build](#anchor-build-containers")
and that the
[workflow templates are populated](#anchor-populate-workflow-templates).

```bash
# Proceed with the run of each sub-workflows (of the full workflow)
argo submit --watch --log just-collect.yml --parameter-file input-2012-tiny-no_db.yaml
# The above results should be in the `junk/stage_1/` sub-directory
argo submit --watch --log just-split.yml   --parameter-file input-2012-tiny-no_db.yaml
# The above results should be in the `junk/stage_2/` sub-directory
argo submit --watch --log just-strip.yml   --parameter-file input-2012-tiny-no_db.yaml
# The above results should be in the `junk/stage_3/` sub-directory
argo submit --watch --log just-import-to-3dcitydb-and-dump.yml --parameter-file input-2012-tiny-import_dump.yaml
# The above results should be in the `junk/stage_4/` sub-directory
# The purpose of following workflow is to assert that above db dump was correct
argo submit --watch --log just-load-dump.yml       --parameter-file input-2012-tiny-import_dump.yaml
argo submit --watch --log just-compute-tileset.yml --parameter-file input-2012-tiny-import_dump.yaml
# The resulting tileset should be located in the `junk/stage_5/` sub-directory
```

In addition to the outputs printed at execution time, you can access to
the execution logs with

```bash
argo list logs | grep -i ^parameters-
argo logs parameters-<generated_string>
```

### <a name='Runningtheworkflowstagebystage:multiplevintagesversion'></a>Running the workflow stage by stage: multiple vintages version

First make sure that the
[containers are build](#anchor-build-containers")
and that the
[workflow templates are populated](#anchor-populate-workflow-templates).

Submission can now be done with

```bash
argo submit --watch --log just-prepare-vintages-boroughs.yml \
            --parameter-file input-loop-in-loop-tiny.yaml
# The above results should be in the junk/stage_1/, junk/stage_2/ and
# junk/stage_3/ sub-directories
```

### <a name='Runningthefullworkflow'></a>Running the full workflow

Notice that you can overload any of the parameters at invocation stage with

```bash
argo submit --watch --log full-workflow.yml \
   --parameter-file workflow_input.yaml \
   -p pattern=BATI
```

### <a name='Runningthefullworkflow-1'></a>Running the full workflow

```bash
argo submit --watch --log full-workflow.yml \
            --parameter-file workflow_input.yaml
```

## <a name='Troubleshooting'></a>Troubleshooting

### <a name='Hungupworkflowpendingstatus'></a>Hung up workflow (pending status)

When a workflow was launched but gets hung up (nothing happens, no output at
the argo level, yet the corresponding pod status as retrieved with `k get pods`
is pending) you might get some debugging information with the command

```bash
k describe pod <pod-name>
```

### <a name='Storagebackendisfull'></a>Storage backend is full

When running the pipeline (with `argo submit`) you might get the following
error message

```bash
Error (exit code 1): failed to put file: Storage backend has reached its 
minimum free disk threshold. Please delete a few objects to proceed
```

According to
[this ansible issue](https://github.com/ansible/awx-operator/issues/609)
(with some clues from
[this minio issue](https://github.com/minio/minio/issues/6795))
this indicates that the minikube file system is probably full. In order to free
some disk space

```bash
yes | minikube ssh "docker system prune"
yes | minikube ssh "docker volume prune"
```

or equivalently

```bash
eval $(minikube docker-env)
yes | docker system prune
yes | docker volume prune
```

### <a name='Incasetheminikubesk8sclustergetscorrupted'></a>In case the minikube's k8s cluster gets corrupted

When using `minikube` and the associated k8s ends up
[SNAFU](https://en.wikipedia.org/wiki/SNAFU)
a [partial](https://stackoverflow.com/questions/53871053/how-to-completely-purge-minikube-config-or-reset-ip-back-to-192-168-99-100)
purge can be obtained with

```bash
minikube delete --purge --all
rm -rf ~/.minikube             # This sometimes really matters !
rm -rf ~/.kube
```

### <a name='Dealingwithusingtheemissaryexecutorerror'></a>Dealing with "using the emissary executor" error

At runtime (i.e. when using `argo submit`) one gets an error message of the
form

```bash
Message: step group deemed errored due to child parameters-[...] 
error: when using the emissary executor you must either explicitly specify
the command, or list the image command in the index
```

This seems to be due to the fact that (starting from argo version > 3.2) the
default executor is
[not docker anymore but emissary](https://argoproj.github.io/argo-workflows/workflow-executors/#emissary-emissary).
Although the
[docker executor is announced as deprecated](https://argoproj.github.io/argo-workflows/workflow-executors/#docker-docker)
we can force (within the configmap) the executor to be `docker` with the
following command

```bash
kubectl -n argo patch cm workflow-controller-configmap -p '{"data": {"containerRuntimeExecutor": "docker"}}'
```

## <a name='Developers'></a>Developers

### <a name='Installutils'></a>Install utils

```bash
# Install kub eval refer to https://www.kubeval.com/installation/
brew install kubeval
```

### <a name='Runningtheexamples'></a>Running the examples

```bash
eval $(minikube docker-env)    # Just in case docker builds get required
argo template create workflow-template/*.yml
argo submit --watch --log Examples/example-3dcitydb-daemon.yml  --parameter-file input-just_db.yaml
argo submit --watch --log  Examples/example-loop-in-loop-through-template-call.yml
...
```

The entrypoint template can be overridden at runtime e.g.

```bash
argo submit --parameter-file input-just_db.yaml --parameter output_dir=junk \
            --watch --log FailingIssues/postgres-pgdata-permission-issue.yml \
            --entrypoint psql-data-permission-fix
```

In the above example notice that using a template as entrypoint of course
requires that all its parameter are defined (the output_dir).

### <a name='Runningtheongoingissuesfailures'></a>Running the ongoing issues/failures

```bash
argo submit --watch --log FailingIssues/postgres-pgdata-permission-issue.yml --parameter-file input-just_db.yaml 
```

that will complain about `chmod: changing permissions of [...] Operation not permitted`.

## <a name='TheprocessofadaptingPythonCallingDocker'></a>The process of adapting PythonCallingDocker

### <a name='CreationofArgoWorkflowsDockerCollect-DockerContext'></a>Creation of ArgoWorkflows/Docker/Collect-DockerContext

Oddly enough the PythonCallingDocker version of the pipeline does not use the
container defined by LyonTemporal/Docker/Collect-DockerContext/. Instead it
choses to re-implement, in Python, the downloading process. The reason for
doing so was to be able to extend the downloading process feature with the
application of patches as well as being able to handle the directory tree
that this Python based version of the pipeline is able to propagate (or deal
with) along the different stages of the pipeline.
