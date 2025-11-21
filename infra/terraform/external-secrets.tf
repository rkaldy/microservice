resource "helm_release" "external_secrets" {
  name             = "external-secrets"
  repository       = "https://charts.external-secrets.io"
  chart            = "external-secrets"
  namespace        = "external-secrets"
  create_namespace = true
  atomic           = true
}

resource "google_service_account" "secrets" {
  for_each = toset(local.cfg.namespaces)

  project      = local.cfg.projectId
  account_id   = "${each.key}-secrets"
  display_name = "GSA for ${each.key} External Secrets"
}

resource "kubernetes_service_account" "secrets" {
  for_each = toset(local.cfg.namespaces)

  metadata {
    name      = "external-secrets"
    namespace = kubernetes_namespace.namespaces[each.key].metadata[0].name
    annotations = {
      "iam.gke.io/gcp-service-account" = google_service_account.secrets[each.key].email
    }
  }
}

resource "google_service_account_iam_member" "secrets_workload_identity" {
  for_each = toset(local.cfg.namespaces)

  service_account_id = google_service_account.secrets[each.key].name
  role   = "roles/iam.workloadIdentityUser"
  member = "serviceAccount:${local.cfg.projectId}.svc.id.goog[${each.key}/external-secrets]"
}

resource "google_project_iam_member" "secrets" {
  for_each = toset(local.cfg.namespaces)

  project  = local.cfg.projectId
  role     = "roles/secretmanager.secretAccessor"
  member   = "serviceAccount:${google_service_account.secrets[each.key].email}"
  condition {
    title       = "${each.key}-prefix"
    description = "Access only to secrets with prefix ${each.key}-"
    expression  = "resource.name.startsWith(\"projects/${data.google_project.project.number}/secrets/${each.key}-\")"
  }
}
