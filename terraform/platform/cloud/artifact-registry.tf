resource "google_artifact_registry_repository" "docker_repo" {
  project       = var.project_id
  location      = var.cluster_location
  repository_id = "docker"
  format        = "DOCKER"
}
