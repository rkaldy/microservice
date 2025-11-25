resource "kubernetes_manifest" "cluster_issuer" {
  manifest = {
    apiVersion = "cert-manager.io/v1",
    kind = "ClusterIssuer",
    metadata = {
      name = "letsencrypt"
    }
    spec = {
      acme = {
        email = var.admin_email,
        server = "https://acme-v02.api.letsencrypt.org/directory",
        privateKeySecretRef = {
          name = "letsencrypt-key"
        },
        solvers = [{
          http01 = {
            ingress = {
              class = "nginx"
            }
          }
        }]
      }
    }
  }
}
