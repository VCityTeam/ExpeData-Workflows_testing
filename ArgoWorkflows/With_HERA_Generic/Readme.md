# Hera framework cluster neutral instructions 

<!-- TOC -->

- [Introduction](#introduction)
- [References](#references)
- [Install Hera and its dependencies](#install-hera-and-its-dependencies)
- [Running the "Hello Hera on PaGoDa" workflow](#running-the-hello-hera-on-pagoda-workflow)
- [Running the hera-workflow examples](#running-the-hera-workflow-examples)
- [Running the CityGMLto3DTiles example](#running-the-citygmlto3dtiles-example)
- [Developers](#developers)
  - [Running the failing or issues](#running-the-failing-or-issues)
  - [IDE notes](#ide-notes)
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

## Running the "Hello Hera on PaGoDa" workflow

```bash
(venv) cd $(git rev-parse --show-cdup)/ArgoWorkflows/Workflows_In_Hera
(venv) export $(xargs < .env)            # Refer above
(venv) python PaGoDa_definition/pagoda_cluster_definition.py
```

When this fails try running things step by step for troubleshooting

```bash
(venv) python PaGoDa_definition/parse_arguments.py
(venv) python PaGoDa_definition/retrieve_access_token.py
(venv) python PaGoDa_definition/assert_pagoda_configmap.py
(venv) python PaGoDa_definition/pagoda_cluster_definition.py 
```

Eventually run

```bash
(venv) python PaGoDa_definition/hello_pagoda.py
```

and assert the workflow ran smoothly with argo UI.

## Running the hera-workflow examples

```bash
(venv) python Tutorial_examples/coin_flip_pagoda.py
(venv) python Tutorial_examples/hello_world_pagoda.py
```

## Running the CityGMLto3DTiles example
As
[stated in the accessing results](../On_PaGoDA_cluster/Readme.md#accessing-results)
the permanent volume holding the resulting files is accessible through a
dedicated pod. Prior to running the CityGMLto3DTiles example make sure that
previous run results won't collide with the new ones and just remove them with
```bash
k -n argo exec -it vcity-pvc-ubuntu-pod -- rm -r /vcity-data/junk/
```

```bash
(venv) python CityGMLto3DTiles_Example/collect.py
(venv) python CityGMLto3DTiles_Example/split_buildings.py
(venv) python CityGMLto3DTiles_Example/strip_gml.py 
# The following is work in progress
(venv) python CityGMLto3DTiles_Example/3dcitydb_start_db.py
```

## Developers

### Running the failing or issues
```bash
(venv) python Failing_Or_Issues/lint_pagoda.py
(venv) python Failing_Or_Issues/string_output_pagoda.py
(venv) python Failing_Or_Issues/flowing_input_parameters_to_output_pagoda.py
(venv) python Failing_Or_Issues/raw_archive_pagoda.py
```

### IDE notes

For those using [vscode](https://en.wikipedia.org/wiki/Visual_Studio_Code) a
workspace is defined in 
'`git rev-parse --show-toplevel`/.vscode/ExpeData-Workflows_testing.code-workspace'

## CLEAN ME
```bash
git clone https://github.com/argoproj-labs/hera-workflows
cd hera-workflows
git checkout 4.4.1    # Has to match the requirements version 
```
