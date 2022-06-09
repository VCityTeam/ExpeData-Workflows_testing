# Running the implemented Argo workflows on a desktop with Minikube

**Page index**
<!-- vscode-markdown-toc -->
* [Cluster preparation](#Clusterpreparation)
  * [Instal dependencies (infrastructure)](#Instaldependenciesinfrastructure)
  * [Expose the CWD as k8s volume](#ExposetheCWDask8svolume)
  * [Assert that the Argo server is operational](#AssertthattheArgoserverisoperational)
  * [Build the required containers](#Buildtherequiredcontainers)
  * [Populate the workflow "library" with workflowTemplates](#PopulatetheworkflowlibrarywithworkflowTemplates)
* [Running the workflows](#Runningtheworkflows)
* [Troubleshooting on the minikube cluster](#Troubleshootingontheminikubecluster)
  * [Storage backend is full](#Storagebackendisfull)
  * [In case the minikube's k8s cluster gets corrupted](#Incasetheminikubesk8sclustergetscorrupted)
  * [Dealing with "using the emissary executor" error](#Dealingwithusingtheemissaryexecutorerror)
* [Developers](#Developers)
  * [Install utils](#Installutils)
  * [Running the examples](#Runningtheexamples)
  * [Running the ongoing issues/failures](#Runningtheongoingissuesfailures)

<!-- vscode-markdown-toc-config
	numbering=false
	autoSave=true
	/vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->

## <a name='Clusterpreparation'></a>Cluster preparation

### <a name='Instaldependenciesinfrastructure'></a>Instal dependencies (infrastructure)

The following was tested on `OSX 12.1` (Monterey) with `Homebrew 3.3.12`

Package install

```bash
brew install kubernetes-cli
kubectl version       # v1.23.2
alias k=kubectl
#
brew install minikube # 1.25.1
#
brew install argo     # 3.2.6
# or when the above fails with "no bottle is available" then use
#      brew install --build-from-source argo
```

Launching minikube

```bash
minikube --memory=8G --cpus 4 start
```

Notice that minikube announces that it downloads some version Kubernetes (e.g.
v1.20.2 preload)

```bash
k create ns argo     # Remember the k=kubectl shell alias (refer above)
export ARGO_NAMESPACE=argo
k config set-context --current --namespace=$ARGO_NAMESPACE
# Start an argo server
k apply -f https://raw.githubusercontent.com/argoproj/argo-workflows/master/manifests/quick-start-postgres.yaml
# and assert the AW controller is running with
k get pod | grep workflow-controller
```

If you wish to work with the UI, you need to open the ad-hoc port-forwarding
with the command

```bash
k -n argo port-forward service/argo-server 2746:2746 &
```

The web UI should be available at `https://localhost:2746`.

Note: the port forward is sometimes documented as

```bash
k -n argo port-forward deployment/argo-server 2746:2746 &
```

whose drawback is that it will fail as soon as the argo-server is respawned.

### <a name='ExposetheCWDask8svolume'></a>Expose the CWD as k8s volume

First expose the CWD (Current Working Directory) to minikube with

```bash
# Note the trailing ampersand of the following command
minikube mount `pwd`:/data/host &
```

The above command allows for the creation of a k8s
[`PersistentVolume` (PV)](https://kubernetes.io/docs/concepts/storage/persistent-volumes/):
refer to the usage of
[`/data/host` within `define_pvc_minikube.yaml`](define_pvc_minikube.yaml#L11).
And based on this PV, a  
[`PersistentVolumeClaim` (PVC)](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
can be defined:
refer to [this line within `define_pvc_minikube.yaml`](define_pvc_minikube.yaml#L16).

The creations of the PV and PVC can be done with

```bash
k -n argo create -f define_pvc_minikube.yaml
```

and asserting that all went well can be done with

```bash
k -n argo get pvc | grep vcity-pvc
k -n argo create -f test_pvc_minikube.yaml 
```

Note: once the above `minikube mount` is issued a workflow could consume/access
it as a volume (refer to
[this example](https://minikube.sigs.k8s.io/docs/handbook/mount/))
with an entry (within an Argo WOrkflow) of the form

```bash
"volumes": [
  {
    "name": "host-mount",
    "hostPath": {
      "path": "/data/host"
    }
  }
]
```

Hence the `minikube mount` target argument (i.e. `/data/host`) has to be
aligned with the workflow volume definition.

### <a name='AssertthattheArgoserverisoperational'></a>Assert that the Argo server is operational

Refer to
[those cluster independent commands](../Run_on_Generic/Readme.md#anchor-assert-argo-server-is-ready).

### <a name='Buildtherequiredcontainers'></a>Build the required containers

<a name="anchor-build-containers"></a>

```bash
# User Minikube's built-in docker command, refer e.g. to
# https://stackoverflow.com/questions/42564058/how-to-use-local-docker-images-with-minikube
eval $(minikube docker-env)
```

and then build the required images by applying
[those docker commands](../Run_on_Generic/Readme.md#anchor-build-containers).

### <a name='PopulatetheworkflowlibrarywithworkflowTemplates'></a>Populate the workflow "library" with workflowTemplates

Run the following [cluster independent argo commands](../Run_on_Generic/Readme.md#anchor-running-the-workflows).

---

## <a name='Runningtheworkflows'></a>Running the workflows

Hopefully workflow submission commands are cluster independent. Apply them
by following
[those instructions](../Run_on_Generic/Readme.md#anchor-running-the-workflows)

---

## <a name='Troubleshootingontheminikubecluster'></a>Troubleshooting on the minikube cluster

Refer to the
[platform independent troubleshooting notes]()

In addition, you might want to check the following Minikube specific
troubleshooting nodes.

### <a name='Storagebackendisfull'></a>Storage backend is full

When running the pipeline (with `argo submit`) you might get the following
error message

```bash
Error (exit code 1): failed to put file: Storage backend has reached its 
minimum free disk threshold. Please delete a few objects to proceed
```

According to
[this ansible issue](https://github.com/ansible/awx-operator/issues/609)
(with some clues from
[this minio issue](https://github.com/minio/minio/issues/6795))
this indicates that the minikube file system is probably full. In order to free
some disk space

```bash
yes | minikube ssh "docker system prune"
yes | minikube ssh "docker volume prune"
```

or equivalently

```bash
eval $(minikube docker-env)
yes | docker system prune
yes | docker volume prune
```

### <a name='Incasetheminikubesk8sclustergetscorrupted'></a>In case the minikube's k8s cluster gets corrupted

When using `minikube` and the associated k8s ends up
[SNAFU](https://en.wikipedia.org/wiki/SNAFU)
a [partial](https://stackoverflow.com/questions/53871053/how-to-completely-purge-minikube-config-or-reset-ip-back-to-192-168-99-100)
purge can be obtained with

```bash
minikube delete --purge --all
rm -rf ~/.minikube             # This sometimes really matters !
rm -rf ~/.kube
```

### <a name='Dealingwithusingtheemissaryexecutorerror'></a>Dealing with "using the emissary executor" error

At runtime (i.e. when using `argo submit`) one gets an error message of the
form

```bash
Message: step group deemed errored due to child parameters-[...] 
error: when using the emissary executor you must either explicitly specify
the command, or list the image command in the index
```

This seems to be due to the fact that (starting from argo version > 3.2) the
default executor is
[not docker anymore but emissary](https://argoproj.github.io/argo-workflows/workflow-executors/#emissary-emissary).
Although the
[docker executor is announced as deprecated](https://argoproj.github.io/argo-workflows/workflow-executors/#docker-docker)
we can force (within the configmap) the executor to be `docker` with the
following command

```bash
kubectl -n argo patch cm workflow-controller-configmap -p '{"data": {"containerRuntimeExecutor": "docker"}}'
```

---

## <a name='Developers'></a>Developers

### <a name='Installutils'></a>Install utils

```bash
# Install kub eval refer to https://www.kubeval.com/installation/
brew install kubeval
```

### <a name='Runningtheexamples'></a>Running the examples

Refer to the
[cluster independent running instructions](../Run_on_Generic/Readme.md#anchor-running-the-examples)

### <a name='Runningtheongoingissuesfailures'></a>Running the ongoing issues/failures

Refer to the
[cluster independent running instructions](../Run_on_Generic/Readme.md#anchor-running-the-failures)
