provider "google" {
  project = var.project_id
  region = var.cluster_location
}

data "google_client_config" "default" {}

data "google_container_cluster" "cluster" {
  name     = var.cluster_name
  location = var.cluster_location
}

data "google_compute_network" "default" {
  name = "default"
}
