# Running the implemented Argo workflows: platform independent commands

**Page index**
<!-- vscode-markdown-toc -->
* [Preparation stage](#Preparationstage)
  * [Asserting argo server is ready](#Assertingargoserverisready)
  * [Defining an argo server namespace](#Defininganargoservernamespace)
  * [Build the required containers](#Buildtherequiredcontainers)
  * [Populate the workflow "library" with workflowTemplates](#PopulatetheworkflowlibrarywithworkflowTemplates)
* [Running the workflows](#Runningtheworkflows)
  * [Running the workflow stage by stage: single vintage version](#Runningtheworkflowstagebystage:singlevintageversion)
  * [Running the workflow stage by stage: multiple vintages version](#Runningtheworkflowstagebystage:multiplevintagesversion)
  * [Running the full workflow](#Runningthefullworkflow)
  * [Running the full workflow](#Runningthefullworkflow-1)
* [Troubleshooting](#Troubleshooting)
  * [Basic troubleshooting](#Basictroubleshooting)
  * [Hung-up/Failing workflow](#Hung-upFailingworkflow)
  * [Dealing with "using the emissary executor" error](#Dealingwithusingtheemissaryexecutorerror)
* [Developers](#Developers)
  * [Running the examples](#Runningtheexamples)
  * [Running the ongoing issues/failures](#Runningtheongoingissuesfailures)
  * [Tools](#Tools)

<!-- vscode-markdown-toc-config
	numbering=false
	autoSave=true
	/vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->

## <a name='Preparationstage'></a>Preparation stage

### <a name='Assertingargoserverisready'></a>Asserting argo server is ready

<a name="anchor-assert-argo-server-is-ready"></a>

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

### <a name='Defininganargoservernamespace'></a>Defining an argo server namespace

<a name="anchor-define-argo-namespace"></a>

```bash
kubectl create ns argo
export ARGO_NAMESPACE=argo
kubectl config use-context --current --namespace=$ARGO_NAMESPACE
```

### <a name='Buildtherequiredcontainers'></a>Build the required containers

<a name="anchor-build-containers"></a>

```bash
docker build -t vcity/collect_lyon_data ../Docker/Collect-DockerContext/
docker build -t vcity/3duse             ../../Docker/3DUse-DockerContext/
docker build -t vcity/citygml2stripper  ../../Docker/CityGML2Stripper-DockerContext/
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

## <a name='Runningtheworkflows'></a>Running the workflows

<a name="anchor-running-the-workflows"></a>

### <a name='Runningtheworkflowstagebystage:singlevintageversion'></a>Running the workflow stage by stage: single vintage version

<a name="anchor-running-the-workflows-stage-by-stage"></a>

First make sure that

* the [containers are properly build](#anchor-build-containers),
* the [workflow templates are populated](#anchor-populate-workflow-templates),
* no preceding running traces will conflict with this new submission by running
  
  ```bash
  \rm -fr junk     # Leading backslash is for inhibiting a possible alias
  ```

  or alternatively modify the `experiment_output_dir` entries of the parameter
  files to point to an empty directory.

Eventually you can proceed with the submissions

```bash
cd $(git rev-parse --show-cdup)/ArgoWorkflows
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
[containers are build](#anchor-build-containers)
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
argo submit --watch --log full-workflow.yml --parameter-file input-2012-tiny-import_dump.yaml
```

### <a name='Runningthefullworkflow-1'></a>Running the full workflow

```bash
argo submit --watch --log full-workflow.yml \
            --parameter-file workflow_input.yaml
```

## <a name='Troubleshooting'></a>Troubleshooting

<a name="anchor-troubleshooting"></a>

### <a name='Basictroubleshooting'></a>Basic troubleshooting

* Assert you are working on the proper cluster (should be `pagoda-test` if you
  stuck to this doc example)

  <a name="anchor-generic-troubleshooting-check-cluster-used"></a>

  ```bash
  kubectl config get-contexts
  ```

* Assert you are working in the proper namespace (should be `argo` if you
  stuck to this doc example)

  <a name="anchor-generic-troubleshooting-check-cluster-used"></a>

  ```bash
  kubectl config view --minify --output 'jsonpath={..namespace}'
  ```

### <a name='Hung-upFailingworkflow'></a>Hung-up/Failing workflow

<a name="anchor-generic-troubleshooting-retrieve-logs"></a>

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

### <a name='Runningtheexamples'></a>Running the examples

<a name="anchor-running-the-examples"></a>

```bash
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

<a name="anchor-running-the-failures"></a>

```bash
argo submit --watch --log FailingIssues/postgres-pgdata-permission-issue.yml --parameter-file input-just_db.yaml 
```

that will complain about `chmod: changing permissions of [...] Operation not permitted`.

### <a name='Tools'></a>Tools

**On OSX**

```bash
brew install lens
```

Launch it as an app. Authenticate (SSO) either with github or google.
Declare the cluster with the "+" button that offers the `sync with files`
sub-button and point it to your `ArgoWorkflows/Run_on_PAGoDA/pagoda_kubeconfig.yaml`
cluster configuration file.
