run:
	docker build -t discord .
	docker run -it --rm \
		-p 8080:8080 \
		-e DISCORD_TOKEN="${DISCORD_TOKEN}" \
		-e DO_TOKEN="${DO_TOKEN}" \
		-e CSGO_GSLT_TOKEN_DM="${CSGO_GSLT_TOKEN_DM}" \
		-e CSGO_GSLT_TOKEN_PUG="${CSGO_GSLT_TOKEN_PUG}" \
		-e CSGO_WEB_TOKEN_DM=${CSGO_WEB_TOKEN_DM} \
		-e CSGO_RCON_PASSWORD="${CSGO_RCON_PASSWORD}" \
		-e CSGO_SV_PASSWORD="${CSGO_SV_PASSWORD}" \
		discord

prom:
	docker run \
    	-p 9090:9090 \
    	-v "/Users/neel/github/infra/csgo/prometheus.yml:/etc/prometheus/prometheus.yml" \
    	prom/prometheus

graf:
	docker run \
		 -p 3000:3000 \
		 grafana/grafana

install:
	helm repo add stable https://kubernetes-charts.storage.googleapis.com
	helm upgrade --install \
		--namespace default \
		-f ../../core/values-ingress.yaml \
		ingress stable/nginx-ingress
	kubectl apply -f https://raw.githubusercontent.com/coreos/prometheus-operator/v0.38.1/bundle.yaml
	kubectl apply -f k8s.yaml
	helm upgrade --install \
		--set sidecar.datasources.enabled=true \
		--set sidecar.dashboards.enabled=true \
		-f values-grafana.yaml \
		grafana stable/grafana
	kubectl get secret --namespace hermes grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
