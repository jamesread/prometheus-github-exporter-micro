# prometheus-github-exporter (micro edition)

This is a GitHub exporter that exports basic metrics from GitHub.

[![Maturity Badge](https://img.shields.io/badge/maturity-Production-brightgreen)](#none)
[![Discord](https://img.shields.io/discord/846737624960860180?label=Discord%20Server)](https://discord.gg/jhYWWpNJ3v)

I wrote this because infinityworks/github-exporter looks to be semi-abandoned - several PRs being ignored, etc. If that project picks up again it may no longer make sense to maintain this exporter.


## Sample output


```ini
github_repo_stars{repo="olivetin/olivetin"} 303.0
github_repo_stars{repo="jamesread/prometheus-gmail-exporter"} 13.0
# HELP github_repo_issues GitHub Repo issues
# TYPE github_repo_issues gauge
github_repo_issues{repo="olivetin/olivetin"} 10.0
github_repo_issues{repo="jamesread/prometheus-gmail-exporter"} 0.0
# HELP github_repo_forks GitHub Repo forks
# TYPE github_repo_forks gauge
github_repo_forks{repo="olivetin/olivetin"} 11.0
github_repo_forks{repo="jamesread/prometheus-gmail-exporter"} 4.0
# HELP github_repo_subscribers GitHub Repo subscribers
# TYPE github_repo_subscribers gauge
github_repo_subscribers{repo="olivetin/olivetin"} 8.0
github_repo_subscribers{repo="jamesread/prometheus-gmail-exporter"} 3.0
```

## Installation / Usage

### Option 1) Docker image

Published on dockerhub as `docker.io/jamesread/prometheus-github-exporter-micro`.

Example usage;

```
docker create --name gh_exporter -p 9171 -e REPOS="olivetin/olivetin,upsilonproject/upsilon-drone,upsilonproject/upsilon-custodian" jamesread/prometheus-github-exporter-micro
```


### Option 2) Clone this repo and run the script.

^^ :-)

## Configuration

Configuration is from environment variables only.

* `REPOS` - a comma-delimited list of repos you want to get metrics for. eg: `export REPOS="olivetin/olivetin,jamesread/prometheus-gmail-exporter"
* `USERS` - a comma-delimited list of users you want to get metrics for (iterate over all repos). eg: `export USERS="jamesread"`
* `PROM_PORT` - The port for the HTTP server to listen on, by default it is `9171`.
* `GITHUB_TOKEN` - A 32-character GitHub API token, otherwise requests to the API as a guest are likely to be rate limited quickly.
* `UPDATE_DELAY_SECONDS` - How long to sleep between updating all repos. Default `3600` seconds.
