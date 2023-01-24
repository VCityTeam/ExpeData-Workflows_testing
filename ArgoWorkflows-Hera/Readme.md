
## References

* [Hera testing notes as done in the Pagoda project](https://gitlab.liris.cnrs.fr/pagoda/pagoda-charts-management/argo-workflows/-/blob/develop/argodocs/docs/heraworkflows.md)
* [Pagoda project Hera examples](https://gitlab.liris.cnrs.fr/pagoda/pagoda-charts-management/argo-workflows/-/tree/develop/hera-script)

## Testing with Minikube

Install minikube and argo server as e.g. [explained here](../Argo_Worfkows_notes_and_tricks.md#starting-an-argo-server-and-an-associated-web-based-ui).
The following assumes that so-called `port forwarding` was configured which can
be asserted with

```bash
export ARGO_SERVER=localhost:2746   # Requires the above port forwarding
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
