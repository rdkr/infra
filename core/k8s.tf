
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

resource "digitalocean_kubernetes_node_pool" "default" {
  cluster_id = digitalocean_kubernetes_cluster.cluster.id
  name       = "s-2vcpu-2gb"
  size       = "s-2vcpu-2gb"
  node_count = 1
}

provider "kubernetes" {
  load_config_file = false
  host             = digitalocean_kubernetes_cluster.cluster.endpoint
  token            = digitalocean_kubernetes_cluster.cluster.kube_config[0].token
  cluster_ca_certificate = base64decode(
    digitalocean_kubernetes_cluster.cluster.kube_config[0].cluster_ca_certificate
  )
}

provider "helm" {
  kubernetes {
    load_config_file = false
    host             = digitalocean_kubernetes_cluster.cluster.endpoint
    token            = digitalocean_kubernetes_cluster.cluster.kube_config[0].token
    cluster_ca_certificate = base64decode(
      digitalocean_kubernetes_cluster.cluster.kube_config[0].cluster_ca_certificate
    )
  }
}

data "helm_repository" "stable" {
  name = "stable"
  url  = "https://kubernetes-charts.storage.googleapis.com"
}
