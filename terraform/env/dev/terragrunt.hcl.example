include "config" {
  path = find_in_parent_folders("config.hcl")
}

include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "..//."
}

dependencies {
  paths = ["../../platform/kubernetes"]
}

inputs = {
  env = basename(get_terragrunt_dir())
  database = {
    type_version        = "POSTGRES_18"
    edition             = "ENTERPRISE"
    cpu                 = 1
    memory              = 3.75
    disk_size           = 10
    disk_autoresize     = true
    deletion_protection = false
    availability_type   = "ZONAL"
    backup_enabled      = false
    backup_time         = "00:30"
    maintenance_day     = 7
    maintenance_hour    = 1
    flags               = {}
  }
}
