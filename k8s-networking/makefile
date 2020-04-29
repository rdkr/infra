install:
	helm repo add stable https://kubernetes-charts.storage.googleapis.com
	helm upgrade -n networking --install \
		-f values-nginx-ingress.yaml \
		nginx-ingress stable/nginx-ingress
	helm upgrade -n networking --install \
		-f values-external-dns.yaml \
		external-dns stable/external-dns

uninstall:
	helm uninstall -n networking external-dns
	# helm uninstall -n networking nginx-ingress
