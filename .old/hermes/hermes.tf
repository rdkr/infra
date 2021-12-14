resource "kubernetes_namespace" "hermes" {
  metadata {
    name = "hermes"
  }
}

resource "helm_release" "postgresql" {
  namespace  = kubernetes_namespace.hermes.metadata[0].name
  name       = "postgresql"
  repository = "https://charts.bitnami.com/bitnami"
  chart      = "postgresql"
}

resource "helm_release" "pgadmin" {
  namespace  = kubernetes_namespace.hermes.metadata[0].name
  name       = "pgadmin"
  repository = "https://helm.runix.net"
  chart      = "pgadmin4"

  set {
    name = "persistentVolume.enabled"
    value = false
  }
  set {
    name  = "env.email"
    value = "neel@rdkr.uk"
  }
}
