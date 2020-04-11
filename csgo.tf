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

resource "digitalocean_volume" "csgo" {
  region                  = "lon1"
  name                    = "csgo"
  size                    = 50
  initial_filesystem_type = "ext4"
}

resource "digitalocean_droplet" "csgo" {
  name     = "csgo"
  image    = "ubuntu-18-04-x64"
  region   = "lon1"
  size     = "s-1vcpu-2gb"
  ssh_keys = [26584190]
  user_data = templatefile("${path.module}/csgo/dm/cloud-config.yaml", {
    csgo_gslt_token    = var.csgo_gslt_token_dm
    csgo_web_token     = var.csgo_web_token
    csgo_rcon_password = var.csgo_rcon_password
  })
}

resource "digitalocean_volume_attachment" "foobar" {
  droplet_id = digitalocean_droplet.csgo.id
  volume_id  = digitalocean_volume.csgo.id
}

resource "cloudflare_record" "cs_rdkr_uk" {
  zone_id = "f6d706e06f5fdb858d0c78bafb1194ec"
  name    = "dm"
  value   = digitalocean_droplet.csgo.ipv4_address
  type    = "A"
  ttl     = 1
}

resource "digitalocean_volume" "pug" {
  region                  = "lon1"
  name                    = "pug.rdkr.uk"
  size                    = 50
  initial_filesystem_type = "ext4"
}

resource "digitalocean_droplet" "pug" {
  name     = "pug.rdkr.uk"
  image    = "ubuntu-18-04-x64"
  region   = "lon1"
  size     = "s-1vcpu-2gb"
  ssh_keys = [26584190]
  user_data = templatefile("${path.module}/csgo/pug/cloud-config.yaml", {
    csgo_gslt_token    = var.csgo_gslt_token_pug
    csgo_rcon_password = var.csgo_rcon_password
    csgo_sv_password   = var.csgo_sv_password
  })
}

resource "digitalocean_volume_attachment" "pug" {
  droplet_id = digitalocean_droplet.csgo.id
  volume_id  = digitalocean_volume.csgo.id
}

resource "cloudflare_record" "pug_rdkr_uk" {
  zone_id = "f6d706e06f5fdb858d0c78bafb1194ec"
  name    = "pug"
  value   = digitalocean_droplet.csgo.ipv4_address
  type    = "A"
  ttl     = 1
}