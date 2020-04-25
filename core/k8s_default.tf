resource "kubernetes_namespace" "concourse" {
  metadata {
    name = "concourse"
  }
}

resource "helm_release" "ingress" {
  name       = "ingress"
  repository = data.helm_repository.stable.metadata[0].name
  chart      = "nginx-ingress"
  values = [
    "${file("values-ingress.yaml")}"
  ]
}
