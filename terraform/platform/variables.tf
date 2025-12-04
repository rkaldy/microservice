variable "project_id" {
  type = string
}

variable "cluster_name" {
  type = string
}

variable "cluster_location" {
  type = string
}

variable "k8s_namespace" {
  type = string
}

variable "admin_email" {
  type = string
}

variable "domain" {
  type = string
}

variable "gitlab_base_url" {
  type = string
}

variable "gitlab_project_path" {
  type = string
}

variable "ci_concurrent_jobs" {
  type = number
}

variable grafana_prometheus_url {
  type = string
}

variable grafana_prometheus_username {
  type = string
}

variable grafana_loki_url {
  type = string
}

variable grafana_loki_username {
  type = string
}
