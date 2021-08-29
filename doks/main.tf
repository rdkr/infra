terraform {
  backend "remote" {
    organization = "rdkr"

    workspaces {
      name = "core"
    }
  }

  required_providers {
    cloudflare = {
      source = "cloudflare/cloudflare"
    }
    digitalocean = {
      source = "digitalocean/digitalocean"
    }
    kubernetes = {
      source = "hashicorp/kubernetes"
    }
    helm = {
      source = "hashicorp/helm"
    }
  }
}

provider "cloudflare" {
  api_token = var.cloudflare_token
}

provider "digitalocean" {
  token = var.do_token
}
