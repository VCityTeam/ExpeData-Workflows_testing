# Experimenting with ArgoWorkflows

**Table of contents**
<!-- TOC -->

- [Running the examples](#running-the-examples)
- [Notes](#notes)
- [References](#references)

<!-- /TOC -->

## Running the examples

|           | Documentation | [Cluster neutral]() | [On Minikube](On_Minikube_cluster/Readme.md) | [On PaGoDA](On_PaGoDA_cluster/Readme.md) |
|-----------|---------------|---|---|---|
| With CLI  | [ArgoWorkflows]() | [CLI/Generic](With_CLI_Generic/Readme.md)  | [CLI/Minikube](Run_with_CLI_on_Minikube.md) | [CLI/PaGoDA](Run_with_CLI_on_PaGoDA.md) |
| With Hera | [Hera docs](https://hera.readthedocs.io/en/stable/) | [Hera/Generic](With_CLI_Generic/Readme.md)  |    | [Hera/PaGoDA](Run_with_HERA_on_PaGoDA/Readme.md) |
| Kubernetes UI | [k8s docs](https://kubernetes.io/docs/home/) |  [N/A](https://en.wikipedia.org/wiki/N/A) | [`minikube dasboard`](https://minikube.sigs.k8s.io/docs/handbook/dashboard/) | [Rancher UI](https://rancher2.pagoda.os.univ-lyon1.fr/ ) | 
| Argo UI   | [AW UI access](https://argoproj.github.io/argo-workflows/argo-server/#access-the-argo-workflows-ui) |  |  | [UI website](https://argowf.pagoda.os.univ-lyon1.fr/) |
| Utils     |  |  |  | [PaGoDa container registry](https://harbor.pagoda.os.univ-lyon1.fr/) | 


## Notes

* [Developers](Developers.md)
* [Upstream technical needs](Workflow_technical_needs.md)
* Argo Workflows [language features](Language_features.md)
* [Argo desktop installation and usage](Installation.md)

* [AW evaluation results](Evaluation_result.md)
* The [process of adapting the pipeline to Argo Workflows](Doc/AdaptationToArgoWorflows.md)
* [TODO list](Todo.md)

## References

* [Argo Workflows github hosted docs](https://argoproj.github.io/argo-workflows/)
* [Official workflow examples](https://github.com/argoproj/argo-workflows/tree/master/examples)
