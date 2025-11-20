provider "google" {
  project = var.project_id
}

data "google_project" "project" {
  project_id = var.project_id
}
