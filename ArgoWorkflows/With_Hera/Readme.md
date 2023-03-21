WARNING: le nom du namespace ou argo est déployé ne peut pas être retrouvé
L'admin doit donner le namespace argo ET le name du service account argo-pagoda-user

Attention le jetton retrouvé par le script python n'est le meme que celui de l'UI argo !

# Hera framework quick evaluation

## Introduction
[Hera is a Python framework](https://github.com/argoproj-labs/hera-workflows)
for constructing and submitting Argo Workflows (refer
[here to alternatives](PythonWrappersAlternative.md)).

## References

* [Hera testing notes as done in the Pagoda project](https://gitlab.liris.cnrs.fr/pagoda/pagoda-charts-management/argo-workflows/-/blob/develop/argodocs/docs/heraworkflows.md)
* [Pagoda project Hera examples](https://gitlab.liris.cnrs.fr/pagoda/pagoda-charts-management/argo-workflows/-/tree/develop/hera-script)

## Running Hera on PaGoDA

1. Retrieve the [PaGoDA cluster credentials at the Kubernetes "level"](../On_PaGoDA_cluster/Readme.md#retrieve-your-cluster-credentials-at-the-kubernetes-level)
   You should now have a `KUBECONFIG` variable (probably pointing to some
   `../Run_on_PAGoDA/pagoda_kubeconfig.yaml` configuration file) and the 
   commands `kubectl get nodes` or `kubectl get pods -n argo` should be 
   returning some content.

### Retrieve your cluster credentials (at k8s level)

Hera accesses the argo-workflows server though the k8s API (as opposed to the
dedicated argo API that is used by the argo CLI). Running an Hera script thus
requires credentials for the argo-workflows server at that level.

```bash
python3 --version     # Say python 3.10.8 
python3 -m venv venv
source venv/bin/activate
(venv) pip install kubernetes
```

You must now ask your cluster admin to provide you with two things
1. the (k8s level) namespace where argo-workflows stands.
2. the service account for accessing argo-workflows.

Because each workflow that you'll launch will require the above information,
place them in environment variables e.g.

```bash
export ARGO_NAMESPACE=argo
export ARGO_SERVICE_ACCOUNT=
```

argo-pagoda-user

### Install Hera (python wrappers)


```bash
(venv) pip install hera-workflows==4.4.1

# The following dependency, refer to  
# https://github.com/argoproj-labs/hera-workflows/blob/main/src/hera/global_config.py#L6
# doesn't seem to be automatically pulled
(venv) pip install typing_extensions
```


```bash
git clone https://github.com/argoproj-labs/hera-workflows
echo 'hera-workflows' >> .gitignore
cd hera-workflows
git checkout 4.3.1
```
