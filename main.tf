terraform {
  backend "remote" {
    organization = "rdkr"

    workspaces {
      name = "infra"
    }
  }
}

variable "do_token" {
  type = string
}

variable "cloudflare_token" {
  type = string
}

provider "digitalocean" {
  token = var.do_token
}

provider "cloudflare" {
  api_token = var.cloudflare_token
}