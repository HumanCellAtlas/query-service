#!/usr/bin/env python
"""
This script outputs GitLab pipeline status.
The GitLab API is expected to be stored in AWS secretsmanager with secret id "$APP_NAME/gitlab-api"
The GitLab Token is expected to be stored in AWS secretsmanager with secret id "$APP_NAME/gitlab-token"
"""
import os, json, re, argparse, subprocess, urllib.parse
import boto3, requests

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("branch", help="Branch to return most recent CI pipeline status")
parser.add_argument("--owner", help="The group or owner of the repository")
parser.add_argument("--repo", help="The repository name")
parser.add_argument("--app-name", help=argparse.SUPPRESS, default=os.environ["APP_NAME"])
args = parser.parse_args()

sm = boto3.client("secretsmanager")

if args.owner is None:
    git_origin = subprocess.check_output(["git", "remote", "get-url", "origin"]).decode()
    args.owner, args.repo, _ = re.search(r"([^\/\:]+)\/(.+?)(\.git)?$", git_origin).groups()

gitlab_api = sm.get_secret_value(SecretId=f"{args.app_name}/gitlab-api")['SecretString']
gitlab_token = sm.get_secret_value(SecretId=f"{args.app_name}/gitlab-token")['SecretString']
slug = urllib.parse.quote_plus(f"{args.owner}/{args.repo}")
r = requests.get(
    f"https://{gitlab_api}/projects/{slug}/pipelines",
    params={"ref": args.branch},
    headers={"Private-Token": gitlab_token},
)
print(json.loads(r.text)[0]['status'])
