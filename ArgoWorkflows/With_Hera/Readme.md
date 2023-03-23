# Hera framework quick evaluation

<!-- TOC -->

- [Introduction](#introduction)
- [References](#references)
- [Running Hera on PaGoDA](#running-hera-on-pagoda)
  - [Retrieve your cluster credentials at k8s level](#retrieve-your-cluster-credentials-at-k8s-level)
  - [Install the python dependencies](#install-the-python-dependencies)
  - [Test your installation by running "Hello world" workflow](#test-your-installation-by-running-hello-world-workflow)
  - [CLEAN ME](#clean-me)

<!-- /TOC -->

## Introduction
[Hera is a Python framework](https://github.com/argoproj-labs/hera-workflows)
for constructing and submitting Argo Workflows (refer
[here to alternatives](PythonWrappersAlternative.md)).

## References

* [Hera testing notes as done in the Pagoda project](https://gitlab.liris.cnrs.fr/pagoda/pagoda-charts-management/argo-workflows/-/blob/develop/argodocs/docs/heraworkflows.md)
* [Pagoda project Hera examples](https://gitlab.liris.cnrs.fr/pagoda/pagoda-charts-management/argo-workflows/-/tree/develop/hera-script)

## Running Hera on PaGoDA

### Retrieve your cluster credentials (at k8s level)

You will first need to retrieve your 
[PaGoDA cluster credentials at the Kubernetes "level"](../On_PaGoDA_cluster/Readme.md#retrieve-your-cluster-credentials-at-the-kubernetes-level)
You should now have a `KUBECONFIG` variable (probably pointing to some
`../Run_on_PAGoDA/pagoda_kubeconfig.yaml` configuration file) and the 
commands `kubectl get nodes` or `kubectl get pods -n argo` should be 
returning some content.

Hera accesses the argo-workflows server though the k8s API (as opposed to the
dedicated argo API that is used by the argo CLI). Running an Hera script thus
requires credentials for the argo-workflows server (accessed at k8s API).

In addition to your `KUBECONFIG` credentials (
[refer e.g. here](../On_PaGoDA_cluster/Readme.md#retrieve-your-cluster-credentials-at-the-kubernetes-level))
you must also ask your cluster admin to provide you with three information
1. the URL designating the argo server
2. the (k8s level) namespace where argo-workflows stands.
3. the service account for accessing argo-workflows.

The first two items can be 
[retrieved through the argo UI](../On_PaGoDA_cluster#retrieve-your-cluster-credentials-at-the-argo-server-level)
and correspond respectively to the `ARGO_SERVER` and the `ARGO_NAMESPACE`
environment variables.
You are left with obtaining the name of service account, for accessing 
argo-workflows, from your cluster admin.

Because each workflow that you'll launch will require the above information,
place them in environment variables e.g.

```bash
export ARGO_SERVER=argowf.pagoda.os.univ-lyon1.fr:443
export ARGO_NAMESPACE=argo
export ARGO_SERVICE_ACCOUNT=argo-pagoda-user
KUBECONFIG=./pagoda_kubeconfig.yaml
```

that you can in turn place within an adaptation of the
[`pagoda_hera_env_vars.bash.tmpl`](pagoda_hera_env_vars.bash.tmpl)
template for a bash script. Name this adaptation e.g. `pagoda_hera_env_vars.bash`) 

### Install the python dependencies

```bash
python3 --version     # Say python 3.10.8 
python3 -m venv venv
source venv/bin/activate
(venv) pip3 install -r requirements.txt   # That install hera-workflows
```

### Test your installation by running "Hello world" workflow

```bash
(venv) source pagoda_hera_env_vars.bash
(venv) python parse_arguments.py
(venv) python examples/hello_world_pagoda.py
```

Check that argo UI displays a new `hello-hera-xxxxx` workflow, wait for the
workflow to finish and check the resulting output logs.

### Run the hera-workflow examples

``bash
(venv) python examples/coin_flip_pagoda.py
```

### Run the CityGMLto3DTiles_Example

``bash
(venv) python Workflow_CityGMLto3DTiles_Example/just_collect.py
```

### CLEAN ME
```bash
git clone https://github.com/argoproj-labs/hera-workflows
cd hera-workflows
git checkout 4.4.1    # Has to match the requirements version 
```
