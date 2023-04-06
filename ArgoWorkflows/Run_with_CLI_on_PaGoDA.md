# Running the implemented Argo workflows on the PAGoDA cluster

<!-- TOC depthfrom:2 orderedlist:false depthto:4 -->

- [Preparing the execution context](#preparing-the-execution-context)
  - [Last steps](#last-steps)
- [Running the workflows](#running-the-workflows)
  - [Running the workflow stage by stage: single vintage version](#running-the-workflow-stage-by-stage-single-vintage-version)
  - [Running the full workflow](#running-the-full-workflow)
  - [Running the full workflow with loop in loop](#running-the-full-workflow-with-loop-in-loop)
- [Accessing the results](#accessing-the-results)

<!-- /TOC -->

## Preparing the execution context

Start with the following steps
- [Prepare the PaGoDA cluster](On_PaGoDA_cluster/Readme.md#cluster-preparation)
- [Assert that the Argo server is operational](With_CLI_Generic/Readme.md#asserting-argo-server-is-ready)
- [Install docker on your desktop](With_CLI_Generic/Readme.md#installing-docker-on-your-desktop) (
  [Here is why](On_PaGoDA_cluster/Readme.md#install-docker-on-your-desktop) 
  you need to do so) 
- [Build the required container images](With_CLI_Generic/Readme.md#build-the-required-containers)
- [Push the container images to the (local) registry](On_PaGoDA_cluster/Readme.md#registering-the-container-images)

### Last steps
Proceed with

- [Defining an argo namespace](With_CLI_Generic/Readme.md#defining-an-argo-server-namespace)
- [Defining I/O volumes](On_PaGoDA_cluster/Readme.md#volumes-and-context-creation)
- [Populating the workflow "library" with workflowTemplates](With_CLI_Generic/Readme.md#populate-the-workflow-library-with-workflowtemplates).

---

## Running the workflows

Alas workflow submission commands are not cluster independent (they should be
[those instructions](With_CLI_Generic/Readme.md#running-the-workflows)).
This is because (for some type of information) the cluster context needs to
be handled over through CLI parameters.

FIXME: document the fact that we cannot use a `--parameter-file context.yaml`
because `argo submit` only accepts a single parameter file and we already
provide the input parameters. Also document that the registry host-name cannot
be passed through a `Configmap` (and why this cannot be).

### Running the workflow stage by stage: single vintage version

Make sure (refer above) that

- [container images are properly build](With_CLI_Generic/Readme.md#build-the-required-containers)
  (this stage [requires docker](On_PaGoDA_cluster/Readme.md#install-docker-on-your-desktop))
- [container images were pushed to the registry](On_PaGoDA_cluster/Readme.md#registering-the-container-images),
- [workflow templates are populated](With_CLI_Generic/Readme.md#populate-the-workflow-library-with-workflowtemplates),
- no preceding running traces will conflict with this new submission by running
  
  ```bash
  \rm -fr junk     # Leading backslash is for inhibiting a possible alias
  ```

  or alternatively modify the `experiment_output_dir` entries of the parameter
  files to point to an empty directory.

Eventually you can proceed with the following submissions

```bash
cd $(git rev-parse --show-cdup)/ArgoWorkflows/Workflow_CityGMLto3DTiles_Example/
# The following environment variable should already be defined within the 
# "On_PaGoDA_cluster/pagoda_argo.bash" shell file
export KUBE_DOCKER_REGISTRY=dockerRegistryHost=harbor.pagoda.os.univ-lyon1.fr/

# Proceed with the run of each sub-workflows (of the full workflow)
argo submit --watch --log just-collect.yml --parameter-file input-2012-tiny-no_db.yaml -p ${KUBE_DOCKER_REGISTRY}
# The above results should be in the `junk/stage_1/` sub-directory
argo submit --watch --log just-split.yml   --parameter-file input-2012-tiny-no_db.yaml -p ${KUBE_DOCKER_REGISTRY}
# The above results should be in the `junk/stage_2/` sub-directory
argo submit --watch --log just-strip.yml   --parameter-file input-2012-tiny-no_db.yaml -p ${KUBE_DOCKER_REGISTRY}
# The above results should be in the `junk/stage_3/` sub-directory
argo submit --watch --log just-import-to-3dcitydb-and-dump.yml --parameter-file input-2012-tiny-import_dump.yaml
# The above results should be in the `junk/stage_4/` sub-directory
# The purpose of following workflow is to assert that above db dump was correct
argo submit --watch --log just-load-dump.yml       --parameter-file input-2012-tiny-import_dump.yaml
argo submit --watch --log just-compute-tileset.yml --parameter-file input-2012-tiny-import_dump.yaml  -p ${KUBE_DOCKER_REGISTRY}
# The resulting tileset should be located in the `junk/stage_5/` sub-directory
```

### Running the full workflow

```bash
argo submit --watch --log full-workflow.yml --parameter-file input-2012-tiny-import_no_dump.yaml -p ${KUBE_DOCKER_REGISTRY}
```

An example with parallel steps

```bash
argo submit --watch --log full-workflow.yml --parameter-file input-2012-small-import_no_dump.yaml -p ${KUBE_DOCKER_REGISTRY}
```

### Running the full workflow with loop in loop

The above workflows (depending on their input) are looping on their `boroughs`
input. The following ones are loop-in-looping on their vintages (outside loop)
and their boroughs (inside loop).

```bash
argo submit --watch --log just-prepare-vintages-boroughs.yml --parameter-file input-loop-in-loop-tiny.yaml -p ${KUBE_DOCKER_REGISTRY}
```

## Accessing the results

Refer to [PaGoDA specific instructions](On_PaGoDA_cluster/Readme.md#accessing-results)

