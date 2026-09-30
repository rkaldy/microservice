provider "kubernetes" {
  host                   = "https://${data.google_container_cluster.cluster.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(
    data.google_container_cluster.cluster.master_auth[0].cluster_ca_certificate
  )
}

resource "kubernetes_namespace" "ns" {
  metadata {
    name = "${var.k8s_namespace}-${var.env}"
  }
}
