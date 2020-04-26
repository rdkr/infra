install:
	helm repo add stable https://kubernetes-charts.storage.googleapis.com
	helm upgrade --namespace monitoring --install \
		-f values-prometheus-operator.yaml \
		prometheus-operator stable/prometheus-operator
	# kubectl apply -f monitoring.yaml

secret:
	kubectl get secret --namespace monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
