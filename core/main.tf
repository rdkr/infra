terraform {
  backend "remote" {
    organization = "rdkr"

    workspaces {
      name = "core"
    }
  }
}

variable "cloudflare_token" {
  type = string
}

provider "cloudflare" {
  api_token = var.cloudflare_token
}

variable "do_token" {
  type = string
}

provider "digitalocean" {
  token = var.do_token
}
