variable "project_id" {
  type        = string
  description = "Google Console Project ID (with numeric postfix)"
}

variable "k8s_namespace" {
  type        = string
  description = "Kubernetes namespace for this project"
}
