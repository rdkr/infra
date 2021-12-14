terraform {
  backend "remote" {
    organization = "rdkr"

    workspaces {
      name = "infra-github"
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
