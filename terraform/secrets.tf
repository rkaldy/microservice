resource "random_string" "bearer_token" {
  length  = 32
  upper   = true
  lower   = true
  numeric = true
  special = false
}

resource "google_secret_manager_secret" "bearer_token" {
  secret_id = "${var.k8s_namespace}-bearer-token"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "bearer_token" {
  secret      = google_secret_manager_secret.bearer_token.id
  secret_data = random_string.bearer_token.result
}
