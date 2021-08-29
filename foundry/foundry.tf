resource "digitalocean_volume" "foundry" {
  region                  = "lon1"
  name                    = "foundry"
  size                    = 10
  initial_filesystem_type = "ext4"
}

resource "digitalocean_droplet" "foundry" {
  count  = var.on ? 1 : 0
  name   = "vtt.rdkr.uk"
  size   = "s-1vcpu-1gb"
  image  = "docker-20-04"
  region = "lon1"
  user_data = templatefile("${path.module}/user_data.yaml", {
    foundry_password  = var.foundry_password,
    foundry_admin_key = var.foundry_admin_key
  })
  ssh_keys   = [29649562]
  monitoring = true
}

resource "digitalocean_volume_attachment" "foundry" {
  count      = var.on ? 1 : 0
  droplet_id = digitalocean_droplet.foundry[0].id
  volume_id  = digitalocean_volume.foundry.id
}

resource "cloudflare_record" "foundry" {
  count   = var.on ? 1 : 0
  zone_id = "f6d706e06f5fdb858d0c78bafb1194ec"
  name    = "vtt.rdkr.uk"
  value   = digitalocean_droplet.foundry[0].ipv4_address
  type    = "A"
  ttl     = 60
}
