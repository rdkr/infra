terraform {
  backend "remote" {
    organization = "rdkr"

    workspaces {
      name = "infra-iac"
    }
  }

  required_providers {
    github = {
      source = "integrations/github"
    }
    tfe = {
    }
  }
}

provider "github" {
  token = var.github_token
}

provider "tfe" {
}
