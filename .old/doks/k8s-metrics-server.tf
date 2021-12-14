resource "helm_release" "metrics_server" {
  namespace  = "kube-system"
  repository = "https://charts.bitnami.com/bitnami"
  chart      = "metrics-server"
  name       = "metrics-server"
  values = [
    "${file("values/values-metrics-server.yaml")}"
  ]
}
