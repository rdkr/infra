resource "digitalocean_droplet" "csgo-base" {
  name     = "csgo-base"
  image    = "ubuntu-18-04-x64"
  region   = "lon1"
  size     = "s-1vcpu-1gb"
  ssh_keys = [26584190]
  user_data = file("${path.module}/cloud-config.yaml")
}
