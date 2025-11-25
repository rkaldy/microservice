variable "project_id" {
  type = string
  description = "Project ID as seen in project list in Google Console"
}

variable "cluster_name" {
  type = string
  description = "GKE cluster name"
}

variable "cluster_location" {
  type = string
  description = "GKE cluster location"
}

variable "k8s_namespaces" {
  type = list(string)
  description = "List of namespaces used by the app. Usually it's app name postfixed by 'dev', 'stage' and 'prod'"
}

variable "admin_email" {
  type = string
  description = "Email used for notifications from Let's Encrypt"
}

variable grafana_prometheus_url {
  type = string
  description = "Grafana endpoint for receiving Prometheus metrics. Copy from Grafana after finishing Logs onboarding."
}

variable grafana_prometheus_username {
  type = string
  description = "Username for receiving Prometheus metrics. Copy from Grafana after finishing Logs onboarding."
}

variable grafana_loki_url {
  type = string
  description = "Grafana endpoint for receiving Loki logs. Copy from Grafana after finishing Logs onboarding."
}

variable grafana_loki_username {
  type = string
  description = "Username for receiving Loki logs. Copy from Grafana after finishing Logs onboarding."
}
