data "google_secret_manager_secret_version" "gitlab_pat" {
  project = var.project_id
  secret  = "gitlab-pat"
  version = "latest"
}

provider "gitlab" {
  token    = data.google_secret_manager_secret_version.gitlab_pat.secret_data
}

data "gitlab_project" "project" {
  path_with_namespace = var.gitlab_project_path
}

resource "gitlab_user_runner" "gitlab_runner" {
  runner_type = "project_type"
  project_id  = data.gitlab_project.project.id
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
    }
  ]
  set_sensitive = [{
      name  = "runnerToken"
      value = gitlab_user_runner.gitlab_runner.token
  }]
}
