data "google_secret_manager_secret_version" "grafana" {
  project = local.cfg.projectId
  secret  = "infra-grafana-password"
  version = "latest"
}


resource "helm_release" "grafana-k8s-monitoring" {
  name             = "grafana-k8s-monitoring"
  repository       = "https://grafana.github.io/helm-charts"
  chart            = "k8s-monitoring"
  namespace        = "monitoring"
  create_namespace = true
  atomic           = true

  values = [file("${path.module}/grafana-monitoring-values.yaml")]

  set {
    name  = "cluster.name"
    value = local.cfg.clusterName
  }

  set {
    name  = "destinations[0].url"
    value = local.cfg.grafana.prometheusUrl
  }

  set_sensitive {
    name  = "destinations[0].auth.username"
    value = local.cfg.grafana.prometheusUsername
  }

  set_sensitive {
    name  = "destinations[0].auth.password"
    value =  data.google_secret_manager_secret_version.grafana.secret_data
  }

  set {
    name  = "destinations[1].url"
    value = local.cfg.grafana.lokiUrl
  }

  set_sensitive {
    name  = "destinations[1].auth.username"
    value = local.cfg.grafana.lokiUsername
  }

  set_sensitive {
    name  = "destinations[1].auth.password"
    value =  data.google_secret_manager_secret_version.grafana.secret_data
  }

  set {
    name  = "alloy-metrics.remoteConfig.enabled"
    value = "false"
  }

  set {
    name  = "alloy-logs.remoteConfig.enabled"
    value = "false"
  }

  set {
    name  = "alloy-metrics.alloy.extraEnv[0].value"
    value = local.cfg.clusterName
  }

  set {
    name  = "alloy-logs.alloy.extraEnv[0].value"
    value = local.cfg.clusterName
  }
}
