build:
	docker build -t rdkr/hermes .

run: build
	docker run -it --rm \
		-p 8080:8080 \
		-e DISCORD_TOKEN="${DISCORD_TOKEN}" \
		-e DO_TOKEN="${DO_TOKEN}" \
		-e CSGO_GSLT_TOKEN_DM="${CSGO_GSLT_TOKEN_DM}" \
		-e CSGO_GSLT_TOKEN_PUG="${CSGO_GSLT_TOKEN_PUG}" \
		-e CSGO_WEB_TOKEN_DM=${CSGO_WEB_TOKEN_DM} \
		-e CSGO_RCON_PASSWORD="${CSGO_RCON_PASSWORD}" \
		-e CSGO_SV_PASSWORD="${CSGO_SV_PASSWORD}" \
		rdkr/hermes python hermes.py

push: build
	docker push rdkr/hermes

install:
	kubectl apply -f k8s.yaml

uninstall:
	kubectl delete -f k8s.yaml

undeploy:
	kubectl delete deployments -n hermes hermes

redeploy: undeploy
	kubectl apply -f k8s.yaml

flow.png: flow.dot
	dot -Tpng flow.dot -o flow.png -Gdpi=300ma
