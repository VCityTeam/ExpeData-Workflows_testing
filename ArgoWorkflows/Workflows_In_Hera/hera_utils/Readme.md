# hera_utils: an embryonic python library of Hera workflows utilities

Helpers for the [Hera Python framework](https://github.com/argoproj-labs/hera)

## Install

```bash
python -m pip install git+https://github.com/VCityTeam/ExpeData-Workflows_testing/tree/master/ArgoWorkflows/Workflows_In_Hera/hera_utils
```

and uninstalling goes

```bash
python -m pip uninstall -y hera_utils        # No confirmation asked
```

Quick importation check

```
python -c "import hera_utils"
```

## For developers

## Setting up the development context

```bash
git clone https://github.com/VCityTeam/ExpeData-Workflows_testing.git
cd ArgoWorkflows/Workflows_In_Hera/hera_utils
python3.10 -m venv venv
 . venv/bin/activate
pip install -r requirements.txt      # Installs hera_utils
```
