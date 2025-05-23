#!/usr/bin/env python

import logging
import os
import json
from datetime import datetime
from time import sleep

from threading import Thread

from dateutil import parser

from prometheus_client import make_wsgi_app, Gauge

import requests


from flask import Flask, Response, request, session, redirect

from werkzeug.middleware.dispatcher import DispatcherMiddleware

import waitress

GAUGE_REGISTRY = {}
REPOS = os.getenv("REPOS", "").split(",")
USERS = os.getenv("USERS", "").split(",")
PROM_PORT = int(os.getenv("PROM_PORT", "9171"))
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

if GITHUB_TOKEN == "":
    REQUEST_HEADERS = {}
else:
    REQUEST_HEADERS = {"Authorization": "token " + GITHUB_TOKEN}


flaskapp = Flask('prometheus-github-exporter-micro')
flaskapp.secret_key = os.urandom(24)


def get_enabled_workflows(repo):
    base_url = "https://api.github.com/repos/" + repo
    url = f"{base_url}/actions/workflows"
    response = requests.get(url, headers=REQUEST_HEADERS)
    response.raise_for_status()
    workflows = response.json().get("workflows", [])
    return [wf for wf in workflows if wf.get("state") == "active"]


def get_latest_run(repo, workflow_id):
    BASE_URL = "https://api.github.com/repos/" + repo

    url = f"{BASE_URL}/actions/workflows/{workflow_id}/runs?per_page=1"
    response = requests.get(url, headers=REQUEST_HEADERS)
    response.raise_for_status()
    runs = response.json().get("workflow_runs", [])
    return runs[0] if runs else None


def get_gauge(repo, metric):
    global GAUGE_REGISTRY

    if metric not in GAUGE_REGISTRY:
        g = Gauge("github_repo_" + metric, 'GitHub Repo ' + metric, [
            "repo",
        ])

        GAUGE_REGISTRY[metric] = g

    return GAUGE_REGISTRY[metric].labels(repo=repo)


def get_workflow_gauge(repo, workflow, metric):
    global GAUGE_REGISTRY

    if metric not in GAUGE_REGISTRY:
        g = Gauge("github_workflow_" + metric, 'GitHub Workflow ' + metric, [
            "repo",
            "workflow",
        ])

        GAUGE_REGISTRY[metric] = g

    return GAUGE_REGISTRY[metric].labels(repo=repo, workflow=workflow)


@flaskapp.route('/')
def index():
    ret = "<h1>Prometheus GitHub Exporter (Micro)</h1>"

    return ret


@flaskapp.route('/readyz')
def readyz():
    return Response("ok", status=200)


def start_waitress():
    logging.info("Starting waitress on port %s", PROM_PORT)

    waitress.serve(flaskapp, host="0.0.0.0", port=PROM_PORT)


def get_repos(repos, users):
    ret = set()

    for repo in repos:
        ret.add(repo)

    for user in users:
        if user == "":
            continue

        page = 1
        while True:
            logging.info(f"Fetching repos for user {user} on page {page}")

            sleep(3)

            res = requests.get(
                f"https://api.github.com/users/{user}/repos?page={page}", headers=REQUEST_HEADERS)

            if res.status_code != 200:
                logging.warning("API HTTP Status: %s", res.status_code)
                continue

            try:
                github_repos = json.loads(res.text)
            except json.decoder.JSONDecodeError as e:
                logging.warning("Failed to decode GitHub JSON: %s", str(e))
                continue

            if not github_repos:
                break

            for github_repo in github_repos:
                ret.add(github_repo['full_name'])

            page += 1

    return ret


def main():
    logging.getLogger().setLevel("INFO")
    logging.info("Starting Prometheus GitHub Exporter (Micro)")

    flaskapp.wsgi_app = DispatcherMiddleware(flaskapp.wsgi_app, {
        '/metrics': make_wsgi_app()
    })

    t = Thread(target=start_waitress)
    t.start()

    update_loop()


def update_loop():
    while True:
        for repo in get_repos(REPOS, USERS):
            logging.info("Updating %s", repo)

            res = requests.get("https://api.github.com/repos/" +
                               repo, headers=REQUEST_HEADERS)

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
            get_gauge(repo, "subscribers").set(
                github_repo['subscribers_count'])

            for wf in get_enabled_workflows(repo):
                logging.info("Updating workflow %s : %s", repo, wf['name'])

                latest_run = get_latest_run(repo, wf['id'])
                if latest_run:
                    logging.info("Latest run for workflow %s: %s",
                                 wf['name'], latest_run['status'])

                    res = 1 if latest_run['conclusion'] == 'success' else 0

                    get_workflow_gauge(repo, wf['name'], "conclusion").set(res)
                    get_workflow_gauge(repo, wf['name'], "updated_at").set(
                        parser.isoparse(latest_run['updated_at']).timestamp()
                    )
                else:
                    logging.warning(
                        "No runs found for workflow %s", wf['name'])

        res = requests.get("https://api.github.com/rate_limit",
                           headers=REQUEST_HEADERS)
        rate_limit = json.loads(res.text)['resources']['core']
        logging.info("Rate limit status: %s out of %s",
                     rate_limit['used'], rate_limit['limit'])

        if rate_limit['used'] >= rate_limit['limit']:
            logging.warning("Rate limit will reset at: %s",
                            datetime.fromtimestamp(rate_limit['reset']))

        sleepySeconds = os.getenv("UPDATE_DELAY_SECONDS", 3600)
        logging.info(
            "Finished updates. Sleeping for %s seconds", sleepySeconds)
        sleep(sleepySeconds)

main()
