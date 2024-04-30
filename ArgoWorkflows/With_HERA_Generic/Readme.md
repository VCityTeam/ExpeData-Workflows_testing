# Hera framework cluster neutral instructions<!-- omit from toc -->

**TOC**

<!-- TOC -->

- [Introduction](#introduction)
- [References](#references)
- [Install Hera and its dependencies](#install-hera-and-its-dependencies)
- [Running workflows](#running-workflows)
  - [Running the "Hello Hera on PaGoDa" workflow](#running-the-hello-hera-on-pagoda-workflow)
  - [Running the hera-workflow examples](#running-the-hera-workflow-examples)
  - [Running the CityGMLto3DTiles example](#running-the-citygmlto3dtiles-example)
- [Developers](#developers)
  - [Running the failing or issues](#running-the-failing-or-issues)
  - [IDE notes](#ide-notes)

<!-- /TOC -->

## Introduction

[Hera is a Python framework](https://github.com/argoproj-labs/hera-workflows)
for constructing and submitting Argo Workflows (refer
[here to alternatives](PythonWrappersAlternative.md)).

## References

- [Hera testing notes as done in the Pagoda project](https://gitlab.liris.cnrs.fr/pagoda/pagoda-charts-management/argo-workflows/-/blob/develop/argodocs/docs/heraworkflows.md)
- [Pagoda project Hera examples](https://gitlab.liris.cnrs.fr/pagoda/pagoda-charts-management/argo-workflows/-/tree/develop/hera-script)

## Install Hera and its dependencies

```bash
cd $(git rev-parse --show-cdup)/ArgoWorkflows/Workflows_In_Hera
python3 --version     # Say python 3.10.8
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt  # Installs hera-workflows among others
```

## Running workflows

### Running the "Hello Hera on PaGoDa" workflow

First assert that the k8s cluster is available, accessible (access rights) and
that the Argo-workflows server is ready for workflow submission

```bash
cd $(git rev-parse --show-cdup)/ArgoWorkflows/Workflows_In_Hera
export $(grep -v '^#' hera.bash | xargs)   # Refer above for hera.bash creation
python PaGoDa_definition/pagoda_environment_definition.py
```

When this fails try running things step by step for troubleshooting

```bash
cd $(git rev-parse --show-cdup)/ArgoWorkflows/Workflows_In_Hera
python PaGoDa_definition/parse_arguments.py
python PaGoDa_definition/k8s_cluster_utils.py
python PaGoDa_definition/argo_server_utils.py
python PaGoDa_definition/pagoda_environment_definition.py
```

Eventually run the testing workflow

```bash
python PaGoDa_definition/test_pagoda_setup.py
```

and assert the workflow ran smoothly with argo UI.

### Running the hera-workflow examples

A few illustrative hera-workflows examples were adapted to the PaGoDa cluster
and placed in the
[`Tutorial_Examples/`](../Workflows_In_Hera/Tutorial_Examples/) sub-directory.
In order to run some of the hera-workflows examples you will need the associated
Hera specific containers that require

- to be pulled
  ([as done for VCity containers](../With_CLI_Generic/Readme.md#buildpull-the-required-containers))
- to be tagged and registered
  ([as done for VCity containers](../On_PaGoDA_cluster/Readme.md#registering-the-container-images))

This process boils down to the following commands

```bash
docker pull argoproj/argosay:v2
docker tag argoproj/argosay:v2 harbor.pagoda.os.univ-lyon1.fr/vcity/argosay:v2
docker login harbor.pagoda.os.univ-lyon1.fr/vcity --username <my-username>
docker push harbor.pagoda.os.univ-lyon1.fr/vcity/argosay:v2
```

You can now proceed with submitting the hera-workflows examples with:

```bash
(venv) cd $(git rev-parse --show-cdup)/ArgoWorkflows/Workflows_In_Hera
(venv) python Tutorial_Examples/hello_world_pagoda.py
(venv) python Tutorial_Examples/hello_world_container_script_pagoda.py
(venv) python Tutorial_Examples/hera_workflow_template__steps.py
(venv) python Tutorial_Examples/hera_coin_flip.py
(venv) python Tutorial_Examples/hera_dag_with_param_passing_pagoda.py
(venv) python Tutorial_Examples/hera_dag_with_script_output_param_passing_pagoda.py
(venv) python Tutorial_Examples/just_sleep_and_exit_pagoda.py
(venv) python Tutorial_Examples/retrieving_pod_ip_pagoda.py
(venv) python Tutorial_Examples/steps_with_callable_container.py
(venv) python Tutorial_Examples/workflow_template_with_output_forwarding.py
(venv) ...
```

### Running the CityGMLto3DTiles example

You can inspect/test this numerical setup by running the following testing
workflow

```
(venv) cd $(git rev-parse --show-cdup)/ArgoWorkflows/Workflows_In_Hera/CityGMLto3DTiles_Example/
(venv) python CityGMLto3DTiles_Example/test_experiment_setup.py
```

As
[stated in the accessing results](../On_PaGoDA_cluster/Readme.md#accessing-results)
the permanent volume holding the resulting files is accessible through a
dedicated pod.
Prior to running the CityGMLto3DTiles example, you might want to make sure that
previous numerical experiment run results won't collide with the new ones
and just remove them with

```bash
k -n argo exec -it vcity-pvc-ubuntu-pod -- rm -r /vcity-data/junk/
```

```bash
(venv) python CityGMLto3DTiles_Example/test_collect.py
(venv) python CityGMLto3DTiles_Example/test_split_buildings.py
(venv) python CityGMLto3DTiles_Example/test_strip_gml.py
```

The next workflow,
[`test_threedcitydb_start_db.py`](../Workflows_In_Hera/CityGMLto3DTiles_Example/test_threedcitydb_start_db.py),
is a test for starting a 3DCityDB database as a service (that is immediately
halted on success). Refer to the
[comments heading `test_threedcitydb_start_db.py`](../Workflows_In_Hera/CityGMLto3DTiles_Example/test_threedcitydb_start_db.py)
for the available behavioral parameters as well as a few usage caveats

```bash
(venv) python CityGMLto3DTiles_Example/test_threedcitydb_start_db.py
```

Then proceed with the last steps

```bash
(venv) python CityGMLto3DTiles_Example/test_import_gml.py
(venv) python CityGMLto3DTiles_Example/test_compute_tileset.py
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
