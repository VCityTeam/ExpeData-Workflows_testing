# Running the implemented Argo workflows: cluster independent commands

<!-- TOC -->

- [Preparation stage](#preparation-stage)
  - [Asserting argo server is ready](#asserting-argo-server-is-ready)
  - [Defining an argo server namespace](#defining-an-argo-server-namespace)
  - [Installing docker on your desktop](#installing-docker-on-your-desktop)
  - [Build/Pull the required containers](#buildpull-the-required-containers)
  - [Populate the workflow "library" with workflowTemplates](#populate-the-workflow-library-with-workflowtemplates)
- [Running the workflows](#running-the-workflows)
  - [Running the workflow stage by stage: single vintage version](#running-the-workflow-stage-by-stage-single-vintage-version)
  - [Running the workflow stage by stage: multiple vintages version](#running-the-workflow-stage-by-stage-multiple-vintages-version)
  - [Running the full workflow](#running-the-full-workflow)
- [Troubleshooting](#troubleshooting)
  - [Basic troubleshooting](#basic-troubleshooting)
  - [Retrieving logs of failing workflow](#retrieving-logs-of-failing-workflow)
  - [Dealing with "using the emissary executor" error](#dealing-with-using-the-emissary-executor-error)
- [Developers](#developers)
  - [Running the examples](#running-the-examples)
  - [Running the ongoing issues/failures](#running-the-ongoing-issuesfailures)

<!-- /TOC -->

## Preparation stage

### Asserting argo server is ready

```bash
# Change to any arbitrary Curent Working Directory (CWD) in order to assert that
# underlying environment variables (e.g. `KUBECONFIG`) do not use relative
# paths: this particularly matters for the PAGoDA execution context
pushd /tmp
# Assert that the underlying kubernetes server is ready
kubectl get nodes      
# Assert that the argo server is present at k8s level (the specified 
# namespace is deployment specific). Notice that this command might
# require some extended access rights
kubectl get pods -n argo | grep workflow-controller
# Check at argo level
argo list
# Retrieve original CWD
popd
```

### Defining an argo server namespace

```bash
kubectl create ns argo
export ARGO_NAMESPACE=argo
kubectl config use-context --current --namespace=$ARGO_NAMESPACE
```

### Installing docker on your desktop

You will need both docker-CLI and the docker-daemon. You might consider
installing [docker-desktop](https://www.docker.com/products/docker-desktop/).
Then assert that `docker` is functional with e.g. `docker info`.

### Build/Pull the required containers

```bash
cd $(git rev-parse --show-cdup)
# FIXME: document why this specific container is appart from others ?!
docker build -t vcity/collect_lyon_data ArgoWorkflows/Docker/Collect-DockerContext/
docker build -t vcity/3duse             Docker/3DUse-DockerContext/
docker build -t vcity/citygml2stripper  Docker/CityGML2Stripper-DockerContext/
docker build --no-cache -f Context/Dockerfile -t vcity/py3dtilers https://github.com/VCityTeam/py3dtilers-docker.git
docker build -t vcity/iphttpcheck       Docker/IpHttpConnectivityCheck-DockerContext/
docker pull refstudycentre/scratch-base:latest
docker pull 3dcitydb/3dcitydb-pg:13-3.1-4.1.0
docker pull 3dcitydb/impexp:4.3.0
docker pull postgres:15.2
```

Notes:

- In case of trouble with the docker builds (e.g. when the build failed
  because of missing disk space) consider using the `--no-cache` flag.

- `refstudycentre/scratch-base` is a really tiny container used as a trick
  (refer to workflow e.g. `Examples/loading-json-fromValue.yml`)

- `docker build` can sort of use the url of sub-directory of git repository 
  (refer e.g. to [this StackOverflow](https://stackoverflow.com/questions/25509828/can-a-docker-build-use-the-url-of-a-git-branch#27295336)). Yet the
  command `docker build --no-cache -t vcity/py3dtilers https://github.com/VCityTeam/py3dtilers-docker.git#:Context` doesn't seem to be effective (Docker version 
  20.10.12).

### Populate the workflow "library" with workflowTemplates

[workflowTemplates](https://github.com/argoproj/argo-workflows/blob/release-3.2/docs/workflow-templates.md)
require a special treat and must be uploaded to the k8s cluster prior to using
(referring) them in a workflow.

```bash
cd $(git rev-parse --show-cdup)/ArgoWorkflows/Workflow_CityGMLto3DTiles_Example/
# Merciless clean-up of possible previous definitions
argo template delete --all
# Add the template references
argo template create workflow-template/database.yml \
                     workflow-template/utils.yml \
                     workflow-template/atomic-steps.yml \
                     workflow-template/aggregated-templaterefs.yml
```

You can assert the `templateRef`s were properly created by e.g. listing them
with `argo template list`.

## Running the workflows

### Running the workflow stage by stage: single vintage version

First make sure that

- the [containers are properly build](#build-the-required-containers),
- the [workflow templates are populated](#populate-the-workflow-library-with-workflowtemplates),
- no preceding running traces will conflict with this new submission by running
  
  ```bash
  \rm -fr junk     # Leading backslash is for inhibiting a possible alias
  ```

  or alternatively modify the `experiment_output_dir` entries of the parameter
  files to point to an empty directory.

Eventually you can proceed with the submissions

```bash
cd $(git rev-parse --show-cdup)/ArgoWorkflows/Workflow_CityGMLto3DTiles_Example/
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

### Running the workflow stage by stage: multiple vintages version

First make sure that the
[containers are build](#build-the-required-containers)
and that the
[workflow templates are populated](#populate-the-workflow-library-with-workflowtemplates).

Submission can now be done with

```bash
argo submit --watch --log just-prepare-vintages-boroughs.yml \
            --parameter-file input-loop-in-loop-tiny.yaml
# The above results should be in the junk/stage_1/, junk/stage_2/ and
# junk/stage_3/ sub-directories
```

### Running the full workflow

Notice that you can overload any of the parameters at invocation stage with

```bash
argo submit --watch --log full-workflow.yml --parameter-file input-2012-tiny-import_dump.yaml
```

```bash
argo submit --watch --log full-workflow.yml  --parameter-file workflow_input.yaml
```

## Troubleshooting

### Basic troubleshooting

- Assert you are working on the proper cluster (should be `pagoda-test` if you
  stuck to this doc example)

  ```bash
  kubectl config get-contexts
  ```

- Assert you are working in the proper namespace (should be `argo` if you
  stuck to this doc example)

  ```bash
  kubectl config view --minify --output 'jsonpath={..namespace}'
  ```

### Retrieving logs of failing workflow

When a workflow was launched but didn't succeed (nothing happens, no output at
the argo level, yet the corresponding pod status as retrieved with `k get pods`
is `pending` or `failing`) you might get some debugging information at the
kubernetes level (as opposed to the argo level) with the commands

```base
argo list logs               # Retrieve the (partial) pod name
kubectl -n argo get pods     # Retrieve the full pod name <the-full-pod-name>
kubectl -n argo describe pod <the-full-pod-name>   # For pod level info
kubectl -n argo logs <the-full-pod-name>           # Logs a k8s level
kubectl -n argo logs <the-full-pod-name> -c main   # Log of the `main` pod
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

### Running the examples

```bash
cd $(git rev-parse --show-cdup)/ArgoWorkflows/Workflow_CityGMLto3DTiles_Example/
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
