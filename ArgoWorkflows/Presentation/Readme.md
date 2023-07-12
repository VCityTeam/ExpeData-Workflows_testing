
# Reseting things

```bash
minikube delete
minikube --memory=8G --cpus 4 start
alias k=kubectl
kubectl create ns argo
export ARGO_NAMESPACE=argo
kubectl config set-context --current --namespace=$ARGO_NAMESPACE
kubectl apply -f https://raw.githubusercontent.com/argoproj/argo-workflows/master/manifests/quick-start-postgres.yaml
kubectl -n argo port-forward service/argo-server 2746:2746
```

```bash
cd <where your scripts are>
minikube mount `pwd`:/data/host &
```
