terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.32.0"
    }
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = "2.36.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "2.17.0"
    }
  }
}
