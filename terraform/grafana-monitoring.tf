data "google_secret_manager_secret_version" "grafana" {
  project = var.project_id
  secret  = "grafana-password"
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

  set = [
    {
      name  = "cluster.name"
      value = var.cluster_name
    },
    {
      name  = "destinations[0].url"
      value = var.grafana_prometheus_url
    },
    {
      name  = "destinations[1].url"
      value = var.grafana_loki_url
    },
    {
      name  = "alloy-metrics.remoteConfig.enabled"
      value = "false"
    },
    {
      name  = "alloy-logs.remoteConfig.enabled"
      value = "false"
    },
    {
      name  = "alloy-metrics.alloy.extraEnv[0].value"
      value = var.cluster_name
    },
    {
      name  = "alloy-logs.alloy.extraEnv[0].value"
      value = var.cluster_name
    }
  ]

  set_sensitive = [
    {
      name  = "destinations[0].auth.username"
      value = var.grafana_prometheus_username
    },
    {
      name  = "destinations[0].auth.password"
      value = data.google_secret_manager_secret_version.grafana.secret_data
    },
    {
      name  = "destinations[1].auth.username"
      value = var.grafana_loki_username
    },
    {
      name  = "destinations[1].auth.password"
      value = data.google_secret_manager_secret_version.grafana.secret_data
    }
  ]
}
