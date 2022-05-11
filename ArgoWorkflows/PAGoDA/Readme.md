# Running the (argo) workflows on the PAGoDA cluster

## Retrieve your cluster credentials at the Kubernetes "level"

The credentials of the Kubernetes cluster of PAGoDA platform must be retrieved
through the rancher server of the PAGoDA platform.
For this web browse to <https://rancher.pagoda.os.univ-lyon1.fr/> and use
the `Keycloak` login mode to provide your LIRIS lab credentials (the ones
defined in LIRIS'
[ldap](https://en.wikipedia.org/wiki/Lightweight_Directory_Access_Protocol)
server).

Among the (Kubernetes) clusters (pre configured by the rancher administrator
select the pagoda cluster (or pagoda-test) e.g. by opening the top-left
menu and selecting the ad-hoc entry within the `Explore Cluster` tab.

Once in the pagoda cluster page, download the `KubeConfig` file associated
to this pagoda cluster. For this use one of the buttons in the right section
of the upper row of the page and place the content e.g. in a
`pagoda_kubeconfig.yaml` file.

Assert you have access to the pagoda (Kubernetes) cluster with the commands

```bash
export KUBECONFIG=pagoda_kubeconfig.yaml
kubectl get nodes
```

## Retrieve your cluster credentials at the Argo (server) "level"

The credentials of the Argo server of the PAGoDA platform must also be retrieved
through the UI of the Argo server of the PAGoDA platform.
For this web browse to <https://argoworkflows.pagoda.os.univ-lyon1.fr/> and use
the `Single Sign ON` login mode to provide your LIRIS lab credentials (just as
for the Kubernetes cluster credential, these credentials are the ones defined
in LIRIS'
[ldap](https://en.wikipedia.org/wiki/Lightweight_Directory_Access_Protocol)
server).

Once logged in, select the `User` Tab within the left icon bar and within the
`Using Your Login With The CLI` section of the page use the `Copy to clipboard`
button to retrieve your credentials and place the content e.g. in a
`pagoda_argo.bash` file.

Optionally, within that `pagoda_argo.bash` you might consider overwriting the
definition of the `KUBECONFIG` (shell) environment variable (that is defaulted
to `/dev/null`) with the path to the above retrieved `pagoda_kubeconfig.yaml`
file.

Additionally, if your argo workflow project uses a namespace that is not default
`argo` namespace you should probably overwrite the `ARGO_NAMESPACE` entry
(of the `pagoda_argo.bash` file) with the name of of your specific argo project.

Assert you have access to the Argo server with the commands

```bash
source ./pagoda_argo.bash
argo list
```

## Incidence of the PAGoDA context on the workflows

### Concerning the http(s) proxy server

In order to retrieve the original data from server located in the
cloud (wget is used), one must configure the site proxy with
([refer here](https://perso.liris.cnrs.fr/emmanuel.coquery/mydocs/docs/ucbl/proxy/)

that boils down to setting the following environment variables

```bash
HTTP_PROXY="http://proxy.univ-lyon1.fr:3128"
HTTPS_PROXY="http://proxy.univ-lyon1.fr:3128"
NO_PROXY="127.0.0.0/16,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,localhost,.novalocal,.univ-lyon1.fr"
```
