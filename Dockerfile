FROM fedora

EXPOSE 9171

RUN dnf update -y && dnf install python python3-requests python3-prometheus_client -y && dnf clean all

COPY prometheus-github-exporter-micro.py /opt

ENTRYPOINT ["/opt/prometheus-github-exporter-micro.py"]
