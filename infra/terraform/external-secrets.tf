resource "google_service_account" "secrets" {
  for_each = toset(var.namespaces)

  project      = var.project_id
  account_id   = "${each.key}-secrets"
  display_name = "GSA for ${each.key} External Secrets"
}

resource "kubernetes_service_account" "secrets" {
  for_each = toset(var.namespaces)

  metadata {
    name      = "external-secrets"
    namespace = kubernetes_namespace.namespaces[each.key].metadata[0].name
    annotations = {
      "iam.gke.io/gcp-service-account" = google_service_account.secrets[each.key].email
    }
  }
}

resource "google_service_account_iam_member" "secrets_workload_identity" {
  for_each = toset(var.namespaces)

  service_account_id = google_service_account.secrets[each.key].name
  role   = "roles/iam.workloadIdentityUser"
  member = "serviceAccount:${var.project_id}.svc.id.goog[${each.key}/external-secrets]"
}

resource "google_project_iam_member" "secrets" {
  for_each = toset(var.namespaces)

  project  = var.project_id
  role     = "roles/secretmanager.secretAccessor"
  member   = "serviceAccount:${google_service_account.secrets[each.key].email}"
  condition {
    title       = "${each.key}-prefix"
    description = "Access only to secrets with prefix ${each.key}-"
    expression  = "resource.name.startsWith(\"projects/${data.google_project.project.number}/secrets/${each.key}-\")"
  }
}

resource "kubernetes_manifest" "secret_store" {
  for_each = toset(var.namespaces)

  manifest = {
    apiVersion = "external-secrets.io/v1"
    kind       = "SecretStore"
    metadata = {
      name      = "external-secrets"
      namespace = each.key
    }
    spec = {
      provider = {
        gcpsm = {
          projectID = var.project_id
          auth = {
            workloadIdentity = {
              serviceAccountRef = {
                name      = "external-secrets"
                namespace = each.key
              }
            }
          }
        }
      }
    }
  }

  depends_on = [
    kubernetes_service_account.secrets
  ]
}
