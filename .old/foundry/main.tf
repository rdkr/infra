terraform {
  backend "remote" {
    organization = "rdkr"

    workspaces {
      name = "foundry"
    }
  }

  required_providers {
    cloudflare = {
      source = "cloudflare/cloudflare"
    }
    digitalocean = {
      source = "digitalocean/digitalocean"
    }
  }
}

provider "cloudflare" {
  api_token = var.cloudflare_token
}

provider "digitalocean" {
  token = var.do_token
}
