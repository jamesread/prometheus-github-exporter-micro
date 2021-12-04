#!/usr/bin/env python

import requests
import logging
import os
import json
from datetime import datetime
from time import sleep

from prometheus_client import start_http_server, Gauge

def get_gauge(repo, metric):
    global GAUGE_REGISTRY 

    if metric not in GAUGE_REGISTRY:
        g = Gauge("github_repo_" + metric, 'GitHub Repo ' + metric, [
            "repo",
        ])

        GAUGE_REGISTRY[metric] = g

    return GAUGE_REGISTRY[metric].labels(repo=repo)

GAUGE_REGISTRY = dict()
REPOS = os.getenv("REPOS", "").split(",")
PROM_PORT = int(os.getenv("PROM_PORT", "9171"))
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

if GITHUB_TOKEN == "": 
    REQUEST_HEADERS = {}
else: 
    REQUEST_HEADERS = {"Authorization": "token " + GITHUB_TOKEN}

logging.getLogger().setLevel(20)
logging.info("Starting prometheus github exporter (micro) on port %s", PROM_PORT)
start_http_server(PROM_PORT)

while True:
    for repo in REPOS:
        logging.info("Updating %s", repo)

        res = requests.get("https://api.github.com/repos/" + repo, headers = REQUEST_HEADERS)

        if res.status_code != 200:
            logging.warning("API HTTP Status: %s", res.status_code)
            continue

        try:
            github_repo = json.loads(res.text)
        except json.decoder.JSONDecodeError as e:
            logging.warning("Failed to decode GitHub JSON: %s", str(e))
            continue

        get_gauge(repo, "stars").set(github_repo['stargazers_count'])
        get_gauge(repo, "issues").set(github_repo['open_issues_count'])
        get_gauge(repo, "forks").set(github_repo['forks'])
        get_gauge(repo, "subscribers").set(github_repo['subscribers_count'])

    
    res = requests.get("https://api.github.com/rate_limit", headers = REQUEST_HEADERS)
    rate_limit = json.loads(res.text)['resources']['core']
    logging.info("Rate limit status: %s out of %s", rate_limit['used'], rate_limit['limit'])

    if rate_limit['used'] >= rate_limit['limit']: 
        logging.warning("Rate limit will reset at: %s", datetime.fromtimestamp(rate_limit['reset']))

    sleepySeconds = os.getenv("UPDATE_DELAY_SECONDS", 3600)
    logging.info("Finished updates. Sleeping for %s seconds", sleepySeconds)
    sleep(sleepySeconds)
