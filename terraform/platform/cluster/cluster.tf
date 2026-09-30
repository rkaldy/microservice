resource "google_container_cluster" "main" {
  project          = var.project_id
  name             = var.cluster_name
  location         = var.cluster_location
  enable_autopilot = true
}
