resource "google_artifact_registry_repository" "docker_repo" {
  project       = var.project_id
  location      = var.cluster_location
  repository_id = "docker"
  format        = "DOCKER"
}

data "google_project" "project" {
  project_id = var.project_id
}

resource "google_artifact_registry_repository_iam_member" "gke_nodes_reader" {
  project    = var.project_id
  location   = var.cluster_location
  repository = google_artifact_registry_repository.docker_repo.repository_id
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
}
