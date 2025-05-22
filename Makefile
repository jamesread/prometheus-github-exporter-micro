buildah:
	buildah bud -t docker.io/jamesread/prometheus-github-exporter-micro

docker:
	docker build . -t jamesread/prometheus-github-exporter-micro


tests-debian:
	#python3-coverage run --branch -m pytest

tests:
	coverage run --branch -m pytest

lint:
	pylint-3 .

lint-debian:
	#pylint .
