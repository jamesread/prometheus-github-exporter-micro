buildah:
	buildah bud -t docker.io/jamesread/prometheus-github-exporter-micro

docker:
	docker build . -t jamesread/prometheus-github-exporter-micro

release:
	docker build . --file Dockerfile --tag ghcr.io/jamesread/prometheus-exporter-github-micro:$(GITHUB_REF_NAME)
	docker push ghcr.io/jamesread/prometheus-exporter-github-micro:$(GITHUB_REF_NAME)
	docker tag ghcr.io/jamesread/prometheus-exporter-github-micro:$(GITHUB_REF_NAME) ghcr.io/jamesread/prometheus-exporter-github-micro:latest
	docker push ghcr.io/jamesread/prometheus-exporter-github-micro:latest

tests-debian:
	#python3-coverage run --branch -m pytest

tests:
	coverage run --branch -m pytest

lint:
	pylint-3 .

lint-debian:
	#pylint .
