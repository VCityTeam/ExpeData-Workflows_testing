# [Argo Workflows](https://argoproj.github.io/argo-workflows/) testing

## Quick starting (on OSX)

We here follow the [quick start guide](https://argoproj.github.io/argo-workflows/quick-start/), that boils down to the following commands

### Dependencies

<a name="install-dependencies"></a>

- Install `minikube` (refer e.g. to [this guide](https://www.serverlab.ca/tutorials/containers/kubernetes/learning-kubernetes-with-minikube-on-osx/))
  
  ```bash
  brew install minikube
  minikube version             # Gave v1.28.0 when these notes where written
  ```

- Install kubernetes CLI command (`kubectl`)

  ```bash
  brew install kubernetes-cli
  kubectl version --short      # Gave v1.26.0 as client version when these notes where written
  ```

- Install [argo CLI](https://github.com/argoproj/argo-workflows/releases/tag/v3.1.11)
  
  ```bash
  brew install argo
  # or when "no bottle is available"
  brew install --build-from-source argo
  argo version                # Gave v3.4.4+3b2626f.dirty when these notes where written
  ```
  
  This is only the argo CLI install: refer below for the installation of the server(s) part.

### Starting Kubernetes with minikube

Start Kubernetes (4G is apparently _not_ sufficient for deploying Argo Workflow son minikube and on a desktop think of turning docker-desktop off in order to avoid "collisions")

```bash
minikube --memory=8G --cpus 4 start
```

Make sure that k8s (server) is up and running

```bash
kubectl version --short       # Should now provide a Server Version (was `v1.25.3` when these notes where written) 
```

Note: when the k8s server was not properly launched (because `minikube start` failed for some reason)
the above command yield an error message of the form `The connection to the server localhost:8080 was refused - did you specify the right host or port?`.

You can now get some k8s syntactic comfort ([kubectl cheat sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)) with

```bash
alias k=kubectl
# Allow for bash completions
source <(kubectl completion bash)
complete -F __start_kubectl k
# or add autocomplete permanently with
# echo "source <(kubectl completion bash)" >> ~/.bashrc 
```

## Install an argo server and an associated web based UI

Define a namespace and use it systematically

```bash
k create ns argo     # Remember the k=kubectl shell alias (refer above)
```

Configure the kubernetes (minikube) as well as the argo-CLI respective environment variables to use that namespace:

```bash
export ARGO_NAMESPACE=argo
k config set-context --current --namespace=$ARGO_NAMESPACE
```

Apply [a manifest](https://stackoverflow.com/questions/55130795/what-is-a-kubernetes-manifest) to set up an argo server

```bash
k apply -n argo -f https://github.com/argoproj/argo-workflows/releases/download/v3.4.4/install.yaml
```

assert the AW controller is running with

```bash
k get pod | grep workflow-controller
```

and open the ad-hoc port-forwarding

```bash
k -n argo port-forward service/argo-server 2746:2746 &
```

in order to access argo UI by opening `https://localhost:2746` (with a web browser for which you might need to accept a "lack of https certificate" exception).

---

## Using Argo through different API

Argo can be used at different levels of API: k8s, curl or a dedicated REST API.

### Using ArgoCLI through/over k8s run an AW example workflow

For this mode of usage, the implicit assumption is that there are no access
rights limitations to use k8s (so that argoCLI can simply "translate" its
commands to k8s without any access rights restrictions).
This generally means you are acting as admin on a k8s server or running on your
desktop.

Submit the workflow and watch (observe) it progress

```bash
argo submit --watch https://raw.githubusercontent.com/argoproj/argo-workflows/master/examples/hello-world.yaml
```

or submit the workflow and watch the logs on the fly

```bash
argo submit --log https://raw.githubusercontent.com/argoproj/argo-workflows/master/examples/hello-world.yaml
```

Once the workflows were submitted, don't hesitate to explore the UI in order to
observe the workflow execution and the associated info (e.g. logs).

Also explore some workflow execution related information with argo CLI

```bash
argo list           # Similar to `kubectl get wf`
argo list -v        # More verbosity: similar to `k -v6 get wf`
k -v9 get wf        # Even more verbosity
argo get @latest    # Provide more info about the last run workflow
argo logs @latest   # Provide its logs
```

Some possibly useful environment variables

```bash
export ARGO_NAMESPACE=argo             # When using a namespace (refer below)
export ARGO_SERVER=localhost:2746      # Do not prefix with http or https
export ARGO_SECURE=true                # Require TLS i.e. https
export ARGO_INSECURE_SKIP_VERIFY=true  # For self signed certificates
# In the unlikely event of using many instances
export ARGO_INSTANCEID=...
```

### Using Argo's REST API to access the argo server

<a name="rest-api-setup"></a>
This argoCLI usage mode most often requires an access token. If we follow the
[AW access token documentation](https://argoproj.github.io/argo-workflows/access-token/),
the creation of such an access tokena role with

```bash
# A role is authorized to access some (limited) verbs and ressources 
k create role argo-user --verb=create,get,list,patch,update,watch --resource=workflows.argoproj.io 
k create sa argo-user        # Note: SA=Service Account
k get sa | grep argo-user    # Asserting the SA was properly created
k get sa argo-user -o yaml   # Ditto but with the associated yaml output

# Bind service account with the role 
k create rolebinding argo-user --role=argo-user --serviceaccount=argo:argo-user

# Eventually we can create the token
k apply -f argo-secret.yml
k get secret argo-user.service-account-token   # Should display the existing token name
```

The created token must be retrieved and stored in the ad-hoc environment
variable for proper usage

```bash
# Retrieve the token
DECODED_TOKEN=$(kubectl get secret argo-user.service-account-token -o=jsonpath='{.data.token}' | base64 --decode)
echo $DECODED_TOKEN                  # Assert this variable is not empty
ARGO_TOKEN="Bearer $DECODED_TOKEN"
echo $ARGO_TOKEN                     # Make sure the token was indeed defined
```

Make sure that access port forwarding was set (refer above) and assert that the
generated token is properly recognized by using the REST API with e.g.

```bash
export ARGO_SERVER='localhost:2746'     # Designate the port forwarded port
curl --insecure https://localhost:2746/api/v1/workflows/argo -H "Authorization: $ARGO_TOKEN"
```

You can also use the created token to
[login through the UI](https://localhost:2746/login) (browse to
`https://localhost:2746/login`). Once authenticated you can browse the
(swagger generated) [argo API documentation](https://localhost:2746/apidocs)
(browse `https://localhost:2746/apidocs`).

In order to use argo CLI (and besides the `ARGO_TOKEN` variable) you will need
to define a bunch of environment variables that you can copy/paste from the
[`Using Your Login With The CLI`](https://localhost:2746/userinfo) section of
the `user` tab of the UI (`https://localhost:2746/userinfo`).Such definitions
usually boil down to

```bash
export ARGO_SERVER='localhost:2746' 
export ARGO_HTTP1=true  
export ARGO_SECURE=true
export ARGO_BASE_HREF=
export ARGO_TOKEN='[REDACTED]'  # Already defined above
export ARGO_NAMESPACE=argo ;    # or whatever your namespace is 
export KUBECONFIG=/dev/null ;   # Just to prevent any fold-back to the k8s API
```

When deploying on a desktop (where) you will also need to define

```bash
export ARGO_INSECURE_SKIP_VERIFY=true   # MUST HAVE : NOT GIVEN WITHIN THE UI LIST 
```

Place those variables in e.g. a `argo_env_vars.bash` file and source it when
needed.

Eventually test that the API is accessible e.g. with

```bash
argo list
```

## Using the Python wrappers

There seems to confusingly exist many sources e.g. (note that [CermakM](https://github.com/CermakM) does not seem to be contributor of the [Argo Project](https://github.com/orgs/argoproj/people) neither of [argoproj-labs](https://github.com/orgs/argoproj-labs/people) and the relationship between the [Argo Project](https://argoproj.github.io/) and [the argoproj-labs organisation](https://github.com/argoproj-labs) does not seem to be documented)

- [CermakM/argo-client-python](https://github.com/CermakM/argo-client-python) that is mirrored to [argoproj-labs/argo-client-python](https://github.com/argoproj-labs/argo-client-python)
- [CermakM/argo-python-dsl](https://github.com/CermakM/argo-python-dsl) that is mirrored to [argoproj-labs/argo-python-dsl](https://github.com/argoproj-labs/argo-python-dsl)
- [Pypi's argo-workflows-sdk](https://pypi.org/project/argo-workflows-sdk/) (mind the the trailing SDK in the name) refers to [CermakM/argo-python-dsl](https://github.com/CermakM/argo-python-dsl) (mind the trailing DSL) for its HomePage.

---

## Argo workflows running on minikube

### Mounting local directory as k8s volume

```bash
minikube mount --v 5 `pwd`:/data/host &
minikube ssh ls /data/host    # OK: the content of the CWD is present
```

Note that strangely enough the volume appears quite oddly at the filesystem
level:

```bash
# The following won't show any occurrence of /data as filesystem
minikube ssh 'df | grep -v overlay | grep -v shm'
minikube ssh 'df /data/host'  # Will display the filesystem as an IP number
```

References:

- <https://minikube.sigs.k8s.io/docs/handbook/persistent_volumes/>
- <https://minikube.sigs.k8s.io/docs/handbook/mount/>
- <https://stackoverflow.com/questions/54993532/how-to-use-kubernetes-persistent-local-volumes-with-minikube-on-osx>
