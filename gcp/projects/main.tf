terraform {
  cloud {
    organization = "rdkr"

    workspaces {
      name = "infra-gcp-projects"
    }
  }
}
locals {
  billing_account = "01894F-E757C8-641803"
}

provider "google" {}

data "google_organization" "rdkr_uk" {
  domain = "rdkr.uk"
}
