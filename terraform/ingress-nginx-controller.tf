resource "helm_release" "ingress_nginx_controller" {
  name             = "ingress-nginx"
  repository       = "https://kubernetes.github.io/ingress-nginx"
  chart            = "ingress-nginx"
  namespace        = "ingress-nginx"
  create_namespace = true
  atomic           = true

  set = [{
    name = "controller.service.type"
    value = "LoadBalancer"
  }]
}
