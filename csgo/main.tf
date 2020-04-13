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

variable "csgo_gslt_token_dm" {
  type = string
}

variable "csgo_gslt_token_pug" {
  type = string
}

variable "csgo_web_token" {
  type = string
}

variable "csgo_rcon_password" {
  type = string
}

variable "csgo_sv_password" {
  type = string
}