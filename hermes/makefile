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
		discord python hermes_control.py

install:
	kubectl apply -f k8s.yaml
