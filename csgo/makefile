run:
	docker build -t discord . 
	docker run -it \
		-e DISCORD_TOKEN="${DISCORD_TOKEN}" \
		-e DO_TOKEN="${DO_TOKEN}" \
		-e CSGO_GSLT_TOKEN="${CSGO_GSLT_TOKEN}" \
		-e CSGO_RCON_PASSWORD="${CSGO_RCON_PASSWORD}" \
		-e CSGO_SV_PASSWORD="${CSGO_SV_PASSWORD}" \
		discord
	
	
