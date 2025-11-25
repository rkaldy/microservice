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

variable "env" {
  type = string
}

variable "database" {
  type = object({
    type_version        = string
    edition             = string
    cpu                 = number
    memory              = number
    disk_size           = number
    disk_autoresize     = bool
    deletion_protection = bool
    availability_type   = string
    backup_enabled      = bool
    backup_time         = string
    maintenance_day     = number
    maintenance_hour    = number
    flags               = map(string)
  })
}
