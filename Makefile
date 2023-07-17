buildah:
	buildah bud -t docker.io/jamesread/prometheus-github-exporter-micro

docker:
	docker build . -t jamesread/prometheus-github-exporter-micro
