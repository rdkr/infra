resource "digitalocean_droplet" "dm" {
  name     = "csgo"
  image    = "ubuntu-18-04-x64"
  region   = "lon1"
  size     = "s-1vcpu-2gb"
  ssh_keys = [26584190]
  user_data = templatefile("${path.module}/dm/cloud-config.yaml", {
    csgo_gslt_token    = var.csgo_gslt_token_dm
    csgo_web_token     = var.csgo_web_token
    csgo_rcon_password = var.csgo_rcon_password
  })
}

resource "digitalocean_droplet" "pug" {
  name     = "pug"
  image    = "ubuntu-18-04-x64"
  region   = "lon1"
  size     = "s-1vcpu-2gb"
  ssh_keys = [26584190]
  user_data = templatefile("${path.module}/pug/cloud-config.yaml", {
    csgo_gslt_token    = var.csgo_gslt_token_pug
    csgo_rcon_password = var.csgo_rcon_password
    csgo_sv_password   = var.csgo_sv_password
  })
}
