install:
	# helm repo add stable https://kubernetes-charts.storage.googleapis.com
	helm upgrade --namespace monitoring --install --atomic \
		-f values-metrics-server.yaml \
		metrics-server stable/metrics-server
	# kubectl apply -f https://raw.githubusercontent.com/coreos/prometheus-operator/release-0.38/example/prometheus-operator-crd/monitoring.coreos.com_alertmanagers.yaml
	# kubectl apply -f https://raw.githubusercontent.com/coreos/prometheus-operator/release-0.38/example/prometheus-operator-crd/monitoring.coreos.com_podmonitors.yaml
	# kubectl apply -f https://raw.githubusercontent.com/coreos/prometheus-operator/release-0.38/example/prometheus-operator-crd/monitoring.coreos.com_prometheuses.yaml
	# kubectl apply -f https://raw.githubusercontent.com/coreos/prometheus-operator/release-0.38/example/prometheus-operator-crd/monitoring.coreos.com_prometheusrules.yaml
	# kubectl apply -f https://raw.githubusercontent.com/coreos/prometheus-operator/release-0.38/example/prometheus-operator-crd/monitoring.coreos.com_servicemonitors.yaml
	# kubectl apply -f https://raw.githubusercontent.com/coreos/prometheus-operator/release-0.38/example/prometheus-operator-crd/monitoring.coreos.com_thanosrulers.yaml
	helm upgrade --namespace monitoring --install --atomic \
		-f values-prometheus-operator.yaml \
		prometheus-operator stable/prometheus-operator
	kubectl apply -f ingress.yaml

secret:
	kubectl get secret --namespace monitoring prometheus-operator-grafana -o jsonpath="{.data.admin-user}" | base64 --decode ; echo
	kubectl get secret --namespace monitoring prometheus-operator-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo

uninstall:
	helm uninstall -n monitoring prometheus-operator
