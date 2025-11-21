provider "google" {
  project = local.cfg.project_id
}

data "google_project" "project" {
  project_id = local.cfg.project_id
}
