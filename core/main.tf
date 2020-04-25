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
