
# data "digitalocean_kubernetes_versions" "cluster" {}

resource "digitalocean_kubernetes_cluster" "cluster" {
  name    = "kubernetes"
  region  = "lon1"
  version = "1.16.6-do.2"

  node_pool {
    name       = "default"
    size       = "s-1vcpu-2gb"
    node_count = 1
  }
}

provider "kubernetes" {
  load_config_file = false
  host             = digitalocean_kubernetes_cluster.cluster.endpoint
  token            = digitalocean_kubernetes_cluster.cluster.kube_config[0].token
  cluster_ca_certificate = base64decode(
    digitalocean_kubernetes_cluster.cluster.kube_config[0].cluster_ca_certificate
  )
}