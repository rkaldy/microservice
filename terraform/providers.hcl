generate "required_providers" {
  path      = "required-providers.generated.tf"
  if_exists = "overwrite_terragrunt"

  contents = <<-EOF
    terraform {
      required_providers {
        google = {
          source  = "hashicorp/google"
          version = "7.12.0"
        }
        google-beta = {
          source  = "hashicorp/google-beta"
          version = "7.12.0"
        }
        kubernetes = {
          source  = "hashicorp/kubernetes"
          version = "2.38.0"
        }
        helm = {
          source  = "hashicorp/helm"
          version = "3.1.0"
        }
        random = {
          source  = "hashicorp/random"
          version = "3.7.2"
        }
        github = {
          source  = "integrations/github"
          version = "6.13.0"
        }
      }
    }
  EOF
}
