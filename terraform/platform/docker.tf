resource "google_artifact_registry_repository" "docker_repo" {
  provider      = google
  project       = var.project_id
  location      = var.cluster_location
  repository_id = "docker"
  format        = "DOCKER"
}
