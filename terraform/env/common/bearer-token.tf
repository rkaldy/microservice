resource "random_password" "bearer_token" {
  length  = 32
  special = false
}

resource "google_secret_manager_secret" "bearer_token" {
  secret_id = "${var.env}-bearer-token"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "bearer_token" {
  secret      = google_secret_manager_secret.bearer_token.id
  secret_data = random_password.bearer_token.result
}
