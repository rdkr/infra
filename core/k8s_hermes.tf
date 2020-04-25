resource "kubernetes_namespace" "hermes" {
  metadata {
    name = "hermes"
  }
}
resource "kubernetes_secret" "hermes" {
    metadata{
        name = "hermes"
    namespace = kubernetes_namespace.hermes.name

    }
  data = {
    username = "admin"


  }
}
