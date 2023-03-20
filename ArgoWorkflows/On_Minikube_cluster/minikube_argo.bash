# By default argo on minikube won't define any account and hence
# authenticated access on argo API (as opposed to k8s API) will
# not work. In this case argo-cli will fold back to using the
# kubectl API. But for this to work we must NOT define any
# ARGO_<...> environment variable except for a possible namespace
export ARGO_NAMESPACE=argo ;# or whatever your namespace is 
unset ARGO_SERVER
unset ARGO_HTTP1
unset ARGO_SECURE
unset ARGO_BASE_HREF
unset ARGO_TOKEN
# Because argo-cli will foldback to kubectl API we must NOT
# redirect kubectl to /dev/null or argo-cli won't work at
# all 
#   export KUBECONFIG=/dev/null ;# recommended
