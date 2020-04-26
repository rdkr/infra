
# data "digitalocean_kubernetes_versions" "cluster" {}

resource "digitalocean_kubernetes_cluster" "cluster" {
  name    = "kubernetes"
  region  = "lon1"
  version = "1.16.6-do.2"

  node_pool {
    name       = "default"
    size       = "s-1vcpu-2gb"
    node_count = 2
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

resource "kubernetes_namespace" "networking" {
  metadata {
    name = "networking"
  }
}

resource "kubernetes_secret" "external_dns" {
  metadata {
    name      = "external-dns"
    namespace = kubernetes_namespace.networking.metadata[0].name

  }
  data = {
    "digitalocean_api_token" = var.do_token
  }
}

resource "kubernetes_namespace" "monitoring" {
  metadata {
    name = "monitoring"
  }
}

resource "kubernetes_namespace" "hermes" {
  metadata {
    name = "hermes"
  }
}

resource "kubernetes_secret" "hermes" {
  metadata {
    name      = "hermes"
    namespace = kubernetes_namespace.hermes.metadata[0].name

  }
  data = {
    "DO_TOKEN" = var.do_token
    "CSGO_GSLT_TOKEN_DM"  = var.CSGO_GSLT_TOKEN_DM
    "CSGO_GSLT_TOKEN_PUG" = var.CSGO_GSLT_TOKEN_PUG
    "CSGO_WEB_TOKEN_DM"   = var.CSGO_WEB_TOKEN_DM
    "CSGO_RCON_PASSWORD"  = var.CSGO_RCON_PASSWORD
    "CSGO_SV_PASSWORD"    = var.CSGO_SV_PASSWORD
    "CSGO_DISCORD_TOKEN"  = var.CSGO_DISCORD_TOKEN
  }
}
