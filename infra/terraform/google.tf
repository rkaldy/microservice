provider "google" {
  project = local.cfg.projectId
}

data "google_project" "project" {
  project_id = local.cfg.projectId
}
