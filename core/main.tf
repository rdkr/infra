terraform {
  backend "remote" {
    organization = "rdkr"

    workspaces {
      name = "core"
    }
  }
}

provider "cloudflare" {
  api_token = var.cloudflare_token
}

provider "digitalocean" {
  token = var.do_token
}

provider "aws" {
  region     = "eu-west-1"
  access_key = var.AWS_ACCESS_KEY_ID
  secret_key = var.AWS_SECRET_ACCESS_KEY
}
