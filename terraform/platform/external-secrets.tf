resource "google_service_account" "secret_store" {
  project      = var.project_id
  account_id   = "secret-store"
  display_name = "GSA for Secret Store"
}

resource "kubernetes_service_account" "secret_store" {
  metadata {
    name        = "secret-store"
    namespace   = "external-secrets"
    annotations = {
      "iam.gke.io/gcp-service-account" = google_service_account.secret_store.email
    }
  }
 }

resource "google_project_iam_member" "secret_store" {
  project  = var.project_id
  role     = "roles/secretmanager.secretAccessor"
  member   = "serviceAccount:${google_service_account.secret_store.email}"
}

resource "google_service_account_iam_member" "secrets_workload_identity" {
  service_account_id = google_service_account.secret_store.name
  role   = "roles/iam.workloadIdentityUser"
  member = "serviceAccount:${var.project_id}.svc.id.goog[external-secrets/secret-store]"
}

resource "kubernetes_manifest" "secret_store" {
  manifest = {
    apiVersion = "external-secrets.io/v1"
    kind       = "ClusterSecretStore"
    metadata = {
      name = "secret-store"
    }
    spec = {
      provider = {
        gcpsm = {
          projectID = var.project_id
          auth = {
            workloadIdentity = {
              serviceAccountRef = {
                name      = "secret-store"
                namespace = "external-secrets"
              }
            }
          }
        }
      }
    }
  }
}
