terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
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
    gitlab = {
      source = "gitlabhq/gitlab"
      version = "18.6.1"
    }
  }
}

module "helm_releases" {
  source = "./helm_releases"
}
