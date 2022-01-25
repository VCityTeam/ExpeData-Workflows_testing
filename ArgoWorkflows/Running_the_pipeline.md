# An Argo Workflows (AW) pipeline implementation test

## Running things

### Installation

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

Note: minikube announces that it downloads Kubernetes v1.20.2 preload (??)

```bash
k create ns argo     # Remember the k=kubectl shell alias (refer above)
export ARGO_NAMESPACE=argo
k config set-context --current --namespace=$ARGO_NAMESPACE
# Start an argo server
k apply -f https://raw.githubusercontent.com/argoproj/argo-workflows/master/manifests/quick-start-postgres.yaml
# and assert the AW controller is running with
k get pod | grep workflow-controller
# open the ad-hoc port-forwarding
k -n argo port-forward deployment/argo-server 2746:2746 &
```

### Mount the current working directory as k8s volume

```bash
minikube mount `pwd`:/data/host &   # Note this is process (hence the ampersand)
```

A workflow can now use this as a volume (refer to 
[this example](https://minikube.sigs.k8s.io/docs/handbook/mount/)) as

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

### Build the required containers

```bash
# User Minikube's built-in docker command, refer e.g. to
# https://stackoverflow.com/questions/42564058/how-to-use-local-docker-images-with-minikube
eval $(minikube docker-env)
docker build -t vcity/collect_lyon_data Docker/Collect-DockerContext/
docker build -t vcity/3duse ../Docker/3DUse-DockerContext/
docker build -t vcity/citygml2stripper ../Docker/CityGML2Stripper-DockerContext/
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

### Populate the workflow library [workflowTemplates](https://github.com/argoproj/argo-workflows/blob/release-3.2/docs/workflow-templates.md)

```bash
argo template create workflow-template/*.yml
```

You can assert the `templateRef`s were properly created by e.g. listing them
with `argo template list`. Note: in case some cleanup is required then
the `argo template delete --all` merciless command might do the trick.

### Run the pipeline

Running the pipeline step by step

```bash
\rm -fr junk     # Remove possible previous results to avoid collisions 
argo submit --watch --log just-collect.yml       --parameter-file input-2012-tiny-no_db.yaml
argo submit --watch --log just-split.yml         --parameter-file input-2012-tiny-no_db.yaml
argo submit --watch --log just-strip.yml         --parameter-file input-2012-tiny-no_db.yaml
argo submit --watch --log just-import-to-3dcitydb-and-dump.yml --parameter-file input-2012-tiny-with_db.yaml
```

```bash
argo submit --watch --log full-workflow.yml \
            --parameter-file workflow_input.yaml
```

In addition to the outputs printed at execution time, you can access to
the execution logs with

```bash
argo list logs | grep -i ^parameters-
argo logs parameters-<generated_string>
```

Notice that you can overload any of the parameters at invocation stage with

```bash
argo submit --watch --log full-workflow.yml \
   --parameter-file workflow_input.yaml \
   -p pattern=BATI
```

### Troubleshooting

### Storage backend is full

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
```

### In case the minikube's k8s cluster gets corrupted

When using `minikube` and the associated k8s ends up
[SNAFU](https://en.wikipedia.org/wiki/SNAFU)
a [partial](https://stackoverflow.com/questions/53871053/how-to-completely-purge-minikube-config-or-reset-ip-back-to-192-168-99-100)
purge can be obtained with

```bash
minikube delete
rm -rf ~/.minikube
rm -rf ~/.kube
```

### Dealing with "using the emissary executor" error

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

## Developers

### Install utils

```bash
# Install kub eval refer to https://www.kubeval.com/installation/
brew install kubeval
```

### Running the examples

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

### Running the ongoing issues/failures

```bash
argo submit --watch --log FailingIssues/postgres-pgdata-permission-issue.yml --parameter-file input-just_db.yaml 
```

that will complain about `chmod: changing permissions of [...] Operation not permitted`.

## The process of adapting PythonCallingDocker

### Creation of ArgoWorkflows/Docker/Collect-DockerContext

Oddly enough the PythonCallingDocker version of the pipeline does not use the
container defined by LyonTemporal/Docker/Collect-DockerContext/. Instead it
choses to re-implement, in Python, the downloading process. The reason for
doing so was to be able to extend the downloading process feature with the
application of patches as well as being able to handle the directory tree
that this Python based version of the pipeline is able to propagate (or deal
with) along the different stages of the pipeline.
