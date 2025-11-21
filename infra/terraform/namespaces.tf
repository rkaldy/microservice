resource "kubernetes_namespace" "namespaces" {
  for_each = toset(local.cfg.namespaces)

  metadata {
    name = each.key
  }
}
