resource "gitlab_user_runner" "gitlab_runner" {
  project_id  = data.gitlab_project.project.id
  runner_type = "project_type"
  description = "Kubernetes buildkit runner"
  tag_list    = ["k8s"]
}

resource "google_service_account" "gitlab_runner" {
  project      = var.project_id
  account_id   = "gitlab-runner"
  display_name = "GSA for Gitlab Runners"
}

resource "google_project_iam_member" "gitlab_runner_artifactregistry" {
  project  = var.project_id
  role     = "roles/artifactregistry.writer"
  member   = "serviceAccount:${google_service_account.gitlab_runner.email}"
}

resource "google_service_account_iam_member" "gitlab_runner_workload_identity" {
  service_account_id = google_service_account.gitlab_runner.name
  role   = "roles/iam.workloadIdentityUser"
  member = "serviceAccount:${var.project_id}.svc.id.goog[gitlab-runner/gitlab-runner]"
}

resource "google_service_account_key" "gitlab_runner" {
  service_account_id = google_service_account.gitlab_runner.name
}

locals {
  docker_config_json = jsonencode({
    auths = {
      "${var.cluster_location}-docker.pkg.dev" = {
        "auth" = base64encode(
          "_json_key:${base64decode(google_service_account_key.gitlab_runner.private_key)}"
        )
      }
    }
  })
}

resource "kubernetes_namespace" "gitlab_runner" {
  metadata {
    name = "gitlab-runner"
  }
}

resource "kubernetes_secret" "gitlab_runner_docker_config" {
  metadata {
    name      = "docker-config"
    namespace = "gitlab-runner"
  }
  type = "Opaque"
  data = {
    "config.json" = local.docker_config_json
  }
}


resource "helm_release" "gitlab_runner" {
  name             = "gitlab-runner"
  repository       = "https://charts.gitlab.io"
  chart            = "gitlab-runner"
  namespace        = "gitlab-runner"
  create_namespace = false
  atomic           = true

  values = [file("${path.module}/gitlab-runner-values.yaml")]

  set = [
    {
      name  = "gitlabUrl"
      value = var.gitlab_base_url
    },
    {
      name = "concurrent"
      value = var.ci_concurrent_jobs
    },
    {
      name = "serviceAccount.annotations.iam\\.gke\\.io/gcp-service-account"
      value = google_service_account.gitlab_runner.email
    },
    {
      name = "jobSecrets[0].name"
      value = kubernetes_secret.gitlab_runner_docker_config.metadata[0].name
    },
    {
      name = "jobSecrets[0].mountPath"
      value = "/docker"
    }
  ]
  set_sensitive = [{
      name  = "runnerToken"
      value = gitlab_user_runner.gitlab_runner.token
  }]
}
