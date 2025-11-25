resource "kubernetes_namespace" "ns" {
  metadata {
    name = "${var.k8s_namespace}-${var.env}"
  }
}
