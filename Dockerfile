FROM fedora

EXPOSE 9171

RUN dnf -y update && \
	dnf -y install \
	python3-requests \
	python3-httplib2 \
	python3-oauth2client \
	python3-pyyaml \
	python3-flask \
	python3-waitress \
	python3-dateutil \
	python3-prometheus_client && \
	dnf clean all

COPY prometheus-github-exporter-micro.py /opt

ENTRYPOINT ["/opt/prometheus-github-exporter-micro.py"]
