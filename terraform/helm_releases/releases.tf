resource "helm_release" "external_secrets" {
  name             = "external-secrets"
  repository       = "https://charts.external-secrets.io"
  chart            = "external-secrets"
  namespace        = "external-secrets"
  create_namespace = true
  atomic           = true
}

resource "helm_release" "cert_manager" {
  name             = "cert-manager"
  repository       = "https://charts.jetstack.io"
  chart            = "cert-manager"
  namespace        = "cert-manager"
  create_namespace = true
  atomic           = true

  set = [
    {
      name = "global.leaderElection.namespace"
      value = "cert-manager"
    },
    {
      name = "crds.enabled"
      value = "true"
    }
  ]
}
