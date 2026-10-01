include "config" {
  path = find_in_parent_folders("config.hcl")
}

include "root" {
  path = find_in_parent_folders("root.hcl")
}

dependencies {
  paths = ["../cluster", "../cloud", "../crds"]
}
