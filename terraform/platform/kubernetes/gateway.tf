resource "kubernetes_namespace" "gateway" {
  metadata {
    name = "gateway"
  }
}

resource "kubernetes_manifest" "gateway" {
  manifest = {
    apiVersion = "gateway.networking.k8s.io/v1"
    kind       = "Gateway"
    metadata = {
      name      = "gateway"
      namespace = kubernetes_namespace.gateway.metadata[0].name
      annotations = {
        "networking.gke.io/certmap" = "certificate-map"
      }
    }
    spec = {
      gatewayClassName = "gke-l7-global-external-managed"
      addresses = [
        {
          type  = "NamedAddress"
          value = "external-ip"
        }
      ]
      listeners = [
        {
          name     = "https-root"
          protocol = "HTTPS"
          port     = 443
          hostname = "${var.domain}"
          allowedRoutes = {
            namespaces = {
              from = "All"
            }
          }
        },
        {
          name     = "https-subdomains"
          protocol = "HTTPS"
          port     = 443
          hostname = "*.${var.domain}"
          allowedRoutes = {
            namespaces = {
              from = "All"
            }
          }
        }

      ]
    }
  }
}
