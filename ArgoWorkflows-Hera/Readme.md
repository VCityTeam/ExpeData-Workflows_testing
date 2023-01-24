# Hera framework quick evaluation

[Hera is a Python framework](https://github.com/argoproj-labs/hera-workflows)
for constructing and submitting Argo Workflows.

For other python wrappers refer
[here](../ArgoWorkflows/ArgoWorkflowsPythonWrappers.md).

## References

* [Hera testing notes as done in the Pagoda project](https://gitlab.liris.cnrs.fr/pagoda/pagoda-charts-management/argo-workflows/-/blob/develop/argodocs/docs/heraworkflows.md)
* [Pagoda project Hera examples](https://gitlab.liris.cnrs.fr/pagoda/pagoda-charts-management/argo-workflows/-/tree/develop/hera-script)

## Running Hera on minikube

### Pre-requisites

Install minikube and argo server as e.g.
[explained here](../ArgoWorkflows/Installation.md#install-dependencies).

Because Hera uses the argo API you then need to
[create and define your argo API environment variables](../ArgoWorkflows/Installation.md#rest-api-setup) and make sure the argo API is accessible with e.g.

```bash
argo list
```

Then, with say python3.10

```bash
python3 --version     # Yields Python 3.10.8 
python3 -m venv venv
source venv/bin/activate
pip install hera-workflows==4.3.1
# The following dependency, refer to  
# https://github.com/argoproj-labs/hera-workflows/blob/main/src/hera/global_config.py#L6
# doesn't seem to be automatically pulled
pip install typing_extensions

git clone https://github.com/argoproj-labs/hera-workflows
echo 'hera-workflows' >> .gitignore
cd hera-workflows
git checkout 4.3.1
```
