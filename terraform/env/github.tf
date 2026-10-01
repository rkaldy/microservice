data "google_secret_manager_secret_version" "github_token" {
  secret = "github-token"
}

provider "github" {
  owner = var.github_user
  token = data.google_secret_manager_secret_version.github_token.secret_data
}

data "google_iam_workload_identity_pool_provider" "github_actions" {
  project                            = var.project_id
  workload_identity_pool_id          = data.google_iam_workload_identity_pool.github_actions.workload_identity_pool_id
  workload_identity_pool_provider_id = "github"
}

resource "github_repository_environment" "environment" {
  repository  = var.github_repo
  environment = var.env
}

locals {
  github_actions_variables = {
    GCP_PROJECT_ID                 = var.project_id
    GKE_CLUSTER_NAME               = var.cluster_name
    GKE_CLUSTER_LOCATION           = var.cluster_location
    GCP_WORKLOAD_IDENTITY_PROVIDER = data.google_iam_workload_identity_pool_provider.github_actions.name
    GCP_SERVICE_ACCOUNT            = google_service_account.github_deployer.email
  }
}

resource "github_actions_environment_variable" "deployment" {
  for_each = local.github_actions_variables

  repository    = var.github_repo
  environment   = github_repository_environment.environment.environment
  variable_name = each.key
  value         = each.value
}
