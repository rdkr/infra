install:
	helm repo add stable https://kubernetes-charts.storage.googleapis.com
	helm upgrade --install \
		--namespace default \
		-f ../../core/values-nginx-ingress.yaml \
		nginx-ingress stable/nginx-ingress
	helm upgrade --install \
		--namespace default \
		-f ../../core/values-ingress.yaml \
		external-dns stable/external-dns
	stable/external-dns
	# kubectl apply -f https://raw.githubusercontent.com/coreos/prometheus-operator/v0.38.1/bundle.yaml
	# kubectl apply -f k8s.yaml
	# helm upgrade --install \
	# 	--set sidecar.datasources.enabled=true \
	# 	--set sidecar.dashboards.enabled=true \
	# 	-f values-grafana.yaml \
	# 	grafana stable/grafana
	# kubectl get secret --namespace hermes grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
