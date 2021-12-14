resource "kubernetes_namespace" "kube_ingress_nginx" {
  metadata {
    name = "kube-ingress-nginx"
  }
}

resource "helm_release" "ingress_nginx" {
  namespace  = kubernetes_namespace.kube_ingress_nginx.metadata[0].name
  repository = "https://kubernetes.github.io/ingress-nginx"
  chart      = "ingress-nginx"
  name       = "ingress-nginx"
  values = [
    "${file("values/values-ingress-nginx.yaml")}"
  ]
}
