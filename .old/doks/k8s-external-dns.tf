resource "kubernetes_namespace" "kube_external_dns" {
  metadata {
    name = "kube-external-dns"
  }
}

resource "kubernetes_secret" "cloudflare_api_token" {
  metadata {
    namespace = kubernetes_namespace.kube_external_dns.metadata[0].name
    name      = "cloudflare-api-token"
  }

  data = {
    cloudflare_api_token = var.do_token
  }
}

resource "helm_release" "external_dns" {
  namespace  = kubernetes_namespace.kube_external_dns.metadata[0].name
  repository = "https://charts.bitnami.com/bitnami"
  chart      = "external-dns"
  name       = "external-dns"
  values = [
    "${file("values/values-external-dns.yaml")}"
  ]
}
