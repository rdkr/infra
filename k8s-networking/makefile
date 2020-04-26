install:
	helm repo add stable https://kubernetes-charts.storage.googleapis.com
	helm upgrade --namespace networking --install \
		-f values-nginx-ingress.yaml \
		nginx-ingress stable/nginx-ingress
	helm upgrade --namespace networking --install \
		-f values-external-dns.yaml \
		external-dns stable/external-dns
