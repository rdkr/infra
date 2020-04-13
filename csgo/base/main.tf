terraform {
  backend "remote" {
    organization = "rdkr"

    workspaces {
      name = "csgo"
    }
  }
}

variable "do_token" {
  type = string
}

provider "digitalocean" {
  token = var.do_token
}
