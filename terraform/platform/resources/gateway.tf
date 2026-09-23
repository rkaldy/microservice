resource "kubernetes_namespace" "gateway" {
  metadata {
    name = "gateway"
  }
}

resource "kubernetes_manifest" "gateway" {
  manifest = {
    "apiVersion" = "gateway.networking.k8s.io/v1"
    "kind"       = "Gateway"
    "metadata" = {
      "name"      = "gateway"
      "namespace" = kubernetes_namespace.gateway.metadata[0].name
      "annotations" = {
        "networking.gke.io/certmap" = google_certificate_manager_certificate_map.certificate_map.name
      }
    }
    "spec" = {
      "gatewayClassName" = "gke-l7-global-external-managed"
      "addresses" = [
        {
          "type"  = "NamedAddress"
          "value" = google_compute_global_address.external_ip.name
        }
      ]
      "listeners" = [
        {
          "name"     = "https"
          "protocol" = "HTTPS"
          "port"     = 443
          "hostname" = "*.${var.domain}"
          "allowedRoutes" = {
            "namespaces" = {
              "from" = "All"
            }
          }
        }
      ]
    }
  }
}
