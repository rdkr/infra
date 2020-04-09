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

variable "srcds_token" {
  type = string
}

provider "digitalocean" {
  token = var.do_token
}

# data "digitalocean_kubernetes_versions" "cluster" {}

# resource "digitalocean_kubernetes_cluster" "cluster" {
#   name    = "prod"
#   region  = "lon1"
#   version = data.digitalocean_kubernetes_versions.cluster.latest_version

#   node_pool {
#     name = "default"
#     size  = "s-1vcpu-2gb"
#     node_count = 1
#   }
# }

# provider "kubernetes" {
#   load_config_file = false
#   host  = digitalocean_kubernetes_cluster.cluster.endpoint
#   token = digitalocean_kubernetes_cluster.cluster.kube_config[0].token
#   cluster_ca_certificate = base64decode(
#   digitalocean_kubernetes_cluster.cluster.kube_config[0].cluster_ca_certificate
#   )
# }

# resource "kubernetes_namespace" "csgo" {
#   metadata {
#     name = "csgo"
#   }
# }

resource "digitalocean_droplet" "csgo" {
  name = "csgo"
  image = "ubuntu-18-04-x64"
  region = "lon1"
  size = "s-1vcpu-1gb"
  ssh_keys = [26584190]
  user_data = templatefile("${path.module}/cloud-config.yaml", {
    srcds_token = var.srcds_token
  })
}

resource "digitalocean_volume" "csgo" {
  region                  = "lon1"
  name                    = "csgo"
  size                    = 50
  initial_filesystem_type = "ext4"
}

resource "digitalocean_volume_attachment" "foobar" {
  droplet_id = digitalocean_droplet.csgo.id
  volume_id  = digitalocean_volume.csgo.id
}

output "ip" {
  value = digitalocean_droplet.csgo.ipv4_address
}

# data "docker_registry_image" "csgo" {
#   name          = "cm2network/csgo:sourcemod"
# }

# resource "docker_image" "csgo" {
#   name          = data.docker_registry_image.csgo.name
#   pull_triggers = [data.docker_registry_image.csgo.sha256_digest]
# }

# resource "docker_container" "csgo" {
#   name = "csgo"
#   image = docker_image.csgo.latest

#   network_mode = "host"
#   env = ["SRCDS_TOKEN=${var.srcds_token}"]

#   volumes {
#     volume_name = "csgo"
#     container_path = "/home/steam/csgo-dedicated"
#   }

#   // required to prevent replace
#   user              = "steam"
#   working_dir       = "/home/steam/csgo-dedicated"
#   log_opts = {
#     max-file = "2"
#     max-size = "25m"
#   }
# }
