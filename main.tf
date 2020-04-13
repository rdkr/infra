
# terraform {
#   backend "remote" {
#     organization = "rdkr"

#     workspaces {
#       name = "dns"
#     }
#   }
# }

provider "digitalocean" {
  token = var.do_token
}

variable "cloudflare_token" {
  type = string
}

provider "cloudflare" {
  api_token = var.cloudflare_token
}
