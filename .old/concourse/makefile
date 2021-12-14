install:
	helm repo add concourse https://concourse-charts.storage.googleapis.com/
	helm upgrade --install \
		--namespace concourse \
		--set persistence.enabled=false \
		concourse concourse/concourse
