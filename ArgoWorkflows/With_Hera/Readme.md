# Hera framework quick evaluation

<!-- TOC -->

- [Introduction](#introduction)
- [References](#references)
- [Running Hera on PaGoDA](#running-hera-on-pagoda)
  - [Retrieve your cluster credentials at k8s level](#retrieve-your-cluster-credentials-at-k8s-level)
  - [Assert the existence of configmap for proxy and persistent volume claim](#assert-the-existence-of-configmap-for-proxy-and-persistent-volume-claim)
  - [Install the python dependencies](#install-the-python-dependencies)
  - [Test your installation by running "Hello world" workflow](#test-your-installation-by-running-hello-world-workflow)
  - [Run the hera-workflow examples](#run-the-hera-workflow-examples)
  - [Run the CityGMLto3DTiles_Example](#run-the-citygmlto3dtiles_example)
  - [Developers](#developers)
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
[retrieved through the argo UI](# retrieve-your-cluster-credentials-at-the-argo-server-level)
and correspond respectively to the `ARGO_SERVER` and the `ARGO_NAMESPACE`
environment variables.
You are left with obtaining the name of service account, for accessing 
argo-workflows, from your cluster admin.

Because each workflow that you'll launch will require the above information,
place them in an environment variables file e.g. `.env` (configure the 
provided [`.env.tmpl`](env.tmpl) file):

```bash
ARGO_SERVER=argowf.pagoda.os.univ-lyon1.fr:443
ARGO_NAMESPACE=argo
ARGO_SERVICE_ACCOUNT=argo-pagoda-user
KUBECONFIG=./pagoda_kubeconfig.yaml
```

Then you "import" that file into your current shell by
- either with the `export $(xargs < .env)`
- or by defining a function (in your `~/.bashrc` or `~/.bash_aliases`) of the
  form
  ```bash
  importenv() {
  set -a
  source "$1"
  set +a
  }
  ```
  and invoking it from your shell.

### Assert the existence of configmap for proxy and persistent volume claim

This is done at k8s level 
[as explained here](../On_PaGoDA_cluster/Readme.md#volumes-and-context-creation)

### Install the python dependencies

```bash
python3 --version     # Say python 3.10.8 
python3 -m venv venv
source venv/bin/activate
(venv) pip3 install -r requirements.txt   # That install hera-workflows
```

### Test your installation by running "Hello world" workflow

```bash
(venv) export $(xargs < .env)            # Refer above
(venv) cd Workflow_PaGoDa_definition
(venv) python pagoda_cluster_definition.py 
```

When this fails try running things step by step

```bash
(venv) python parse_arguments.py
(venv) python retrieve_access_token.py
(venv) python assert_pagoda_configmap.py
(venv) python pagoda_cluster_definition.py 
```

Eventually run

```bash
(venv) python hello_pagoda.py
```

and assert the workflow ran smoothly with argo UI.

### Run the hera-workflow examples

```bash
(venv) python Workflow_examples/coin_flip_pagoda.py
```

### Run the CityGMLto3DTiles_Example

```bash
(venv) python Workflow_CityGMLto3DTiles_Example/just_collect.py
```

### Developers

For those using [vscode](https://en.wikipedia.org/wiki/Visual_Studio_Code) a
workspace is defined in 
'`git rev-parse --show-toplevel`/.vscode/ExpeData-Workflows_testing.code-workspace'

### CLEAN ME
```bash
git clone https://github.com/argoproj-labs/hera-workflows
cd hera-workflows
git checkout 4.4.1    # Has to match the requirements version 
```
