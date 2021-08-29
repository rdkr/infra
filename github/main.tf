terraform {
  backend "remote" {
    organization = "rdkr"

    workspaces {
      name = "tf-cloud"
    }
  }

  required_providers {
    github = {
      source = "integrations/github"
    }
  }
}

provider "github" {
  token = var.github_token
}
