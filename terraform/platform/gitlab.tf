data "google_secret_manager_secret_version" "gitlab_pat" {
  project = var.project_id
  secret  = "gitlab-pat"
  version = "latest"
}

provider "gitlab" {
  token    = data.google_secret_manager_secret_version.gitlab_pat.secret_data
}

data "gitlab_project" "project" {
  path_with_namespace = var.gitlab_project_path
}

resource "gitlab_project_variable" "docker_registry" {
  project   = data.gitlab_project.project.id
  key       = "DOCKER_REGISTRY"
  value     = "${google_artifact_registry_repository.docker_repo.location}-docker.pkg.dev/${google_artifact_registry_repository.docker_repo.project}/${google_artifact_registry_repository.docker_repo.repository_id}"
}

resource "gitlab_project_variable" "docker_image" {
  project   = data.gitlab_project.project.id
  key       = "DOCKER_IMAGE"
  value     = var.k8s_namespace
}
