buildah:
	buildah bud -t docker.io/jamesread/prometheus-github-exporter-micro

docker:
	docker build . -t jamesread/prometheus-github-exporter-micro

release:
	docker build . --file Dockerfile --tag ghcr.io/jamesread/prometheus-exporter-github-micro:$(RELEASE_VERSION)
	docker push ghcr.io/jamesread/prometheus-exporter-github-micro:$(RELEASE_VERSION)
	docker tag ghcr.io/jamesread/prometheus-exporter-github-micro:$(RELEASE_VERSION) ghcr.io/jamesread/prometheus-exporter-github-micro:latest
	docker push ghcr.io/jamesread/prometheus-exporter-github-micro:latest

tests-debian:
	#python3-coverage run --branch -m pytest

tests:
	coverage run --branch -m pytest

lint:
	pylint-3 .

lint-debian:
	#pylint .
