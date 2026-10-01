data "google_iam_workload_identity_pool" "github_actions" {
  project                   = var.project_id
  workload_identity_pool_id = "github"
}

resource "google_service_account" "github_deployer" {
  project      = var.project_id
  account_id   = "${var.k8s_namespace}-${var.env}-gha"
}

resource "google_service_account_iam_member" "github_identity" {
  service_account_id = google_service_account.github_deployer.name
  role               = "roles/iam.workloadIdentityUser"
  member = "principal://iam.googleapis.com/${data.google_iam_workload_identity_pool.github_actions.name}/subject/repo:${var.github_user}/${var.github_repo}:environment:${var.env}"
}

resource "google_artifact_registry_repository_iam_member" "github_deployer" {
  project    = var.project_id
  location   = var.cluster_location
  repository = "docker"
  role   = "roles/artifactregistry.writer"
  member = "serviceAccount:${google_service_account.github_deployer.email}"
}

resource "google_project_iam_member" "github_cluster_viewer" {
  project = var.project_id
  role    = "roles/container.clusterViewer"
  member  = "serviceAccount:${google_service_account.github_deployer.email}"
}

resource "google_project_iam_member" "github_service_usage" {
  project = var.project_id
  role    = "roles/serviceusage.serviceUsageConsumer"
  member  = "serviceAccount:${google_service_account.github_deployer.email}"
}

resource "kubernetes_role_binding" "github_deployer" {
  metadata {
    name      = "github-deployer"
    namespace = kubernetes_namespace.ns.metadata[0].name
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "admin"
  }
  subject {
    api_group = "rbac.authorization.k8s.io"
    kind      = "User"
    name      = google_service_account.github_deployer.email
  }
}

resource "kubernetes_role" "github_deployer_custom_resources" {
  metadata {
    name      = "github-deployer-custom-resources"
    namespace = kubernetes_namespace.ns.metadata[0].name
  }

  rule {
    api_groups = ["gateway.networking.k8s.io"]
    resources  = ["httproutes"]
    verbs      = ["get", "list", "watch", "create", "update", "patch", "delete"]
  }

  rule {
    api_groups = ["external-secrets.io"]
    resources  = ["externalsecrets"]
    verbs      = ["get", "list", "watch", "create", "update", "patch", "delete"]
  }
}

resource "kubernetes_role_binding" "github_deployer_custom_resources" {
  metadata {
    name      = "github-deployer-custom-resources"
    namespace = kubernetes_namespace.ns.metadata[0].name
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role.github_deployer_custom_resources.metadata[0].name
  }

  subject {
    api_group = "rbac.authorization.k8s.io"
    kind      = "User"
    name      = google_service_account.github_deployer.email
  }
}
