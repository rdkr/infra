resource "kubernetes_namespace" "hermes" {
  metadata {
    name = "hermes"
  }
}
resource "kubernetes_secret" "hermes" {
    namespace = kubernetes_namespace.hermes.name
  data = {
    username = "admin"


  }
}
