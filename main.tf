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

data "digitalocean_kubernetes_versions" "cluster" {}

resource "digitalocean_kubernetes_cluster" "cluster" {
  name    = "prod"
  region  = "lon1"
  version = data.digitalocean_kubernetes_versions.cluster.latest_version

  node_pool {
    name = "default"
    size  = "s-1vcpu-2gb"
    node_count = 1
  }
}

provider "kubernetes" {
  load_config_file = false
  host  = digitalocean_kubernetes_cluster.cluster.endpoint
  token = digitalocean_kubernetes_cluster.cluster.kube_config[0].token
  cluster_ca_certificate = base64decode(
  digitalocean_kubernetes_cluster.cluster.kube_config[0].cluster_ca_certificate
  )
}
