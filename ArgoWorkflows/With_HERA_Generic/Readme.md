# Hera framework quick evaluation

<!-- TOC -->

- [Introduction](#introduction)
- [References](#references)
- [Install Hera and its dependencies](#install-hera-and-its-dependencies)
- [Test your installation by running the "Hello Hera on PaGoDa" workflow](#test-your-installation-by-running-the-hello-hera-on-pagoda-workflow)
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


## Install Hera and its dependencies

```bash
python3 --version     # Say python 3.10.8 
python3 -m venv venv
source venv/bin/activate
(venv) pip3 install -r requirements.txt   # That install hera-workflows
```

## Test your installation by running the "Hello Hera on PaGoDa" workflow

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

## Run the hera-workflow examples

```bash
(venv) python Workflow_examples/coin_flip_pagoda.py
```

## Run the CityGMLto3DTiles_Example

```bash
(venv) python Workflow_CityGMLto3DTiles_Example/just_collect.py
```

## Developers

For those using [vscode](https://en.wikipedia.org/wiki/Visual_Studio_Code) a
workspace is defined in 
'`git rev-parse --show-toplevel`/.vscode/ExpeData-Workflows_testing.code-workspace'

## CLEAN ME
```bash
git clone https://github.com/argoproj-labs/hera-workflows
cd hera-workflows
git checkout 4.4.1    # Has to match the requirements version 
```
