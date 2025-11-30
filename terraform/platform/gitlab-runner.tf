resource "gitlab_user_runner" "gitlab_runner" {
  runner_type = "project_type"
  project_id  = data.gitlab_project.project.id
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


resource "helm_release" "gitlab_runner" {
  name             = "gitlab-runner"
  repository       = "https://charts.gitlab.io"
  chart            = "gitlab-runner"
  namespace        = "gitlab-runner"
  create_namespace = true
  atomic           = true

  values = [file("${path.module}/gitlab-runner-values.yaml")]

  set = [
    {
      name  = "gitlabUrl"
      value = var.gitlab_base_url
    },
    {
      name = "replicas"
      value = var.ci_replicas
    },
    {
      name = "concurrent"
      value = var.ci_concurrent_jobs
    },
    {
      name = "serviceAccount.annotations.iam\\.gke\\.io/gcp-service-account"
      value = google_service_account.gitlab_runner.email
    }
  ]
  set_sensitive = [{
      name  = "runnerToken"
      value = gitlab_user_runner.gitlab_runner.token
  }]
}
