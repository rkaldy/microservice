variable "project_id" {
  type = string
}

variable "cluster_name" {
  type = string
}

variable "cluster_location" {
  type = string
}

variable "kubernetes_context" {
  type = string
}


variable "namespaces" {
  type = list(string)
}


variable "grafana_prometheus_url" {
  type    = string
}

variable "grafana_prometheus_username" {
  type    = string
}

variable "grafana_loki_url" {
  type    = string
}

variable "grafana_loki_username" {
  type    = string
}
