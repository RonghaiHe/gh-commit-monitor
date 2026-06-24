#!/usr/bin/env python3
"""
GitHub Daily Commit Monitor
Fetches commits from the last 24 hours and sends a daily email report.
"""

import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, timezone


def load_config_from_file(filename: str = ".env") -> dict:
    """Load configuration from .env file."""
    config = {}
    if os.path.exists(filename):
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
    return config


def get_commits_from_repo(repo: str, since: datetime) -> list:
    """Fetch commits from a repository since a given datetime."""
    url = f"https://api.github.com/repos/{repo}/commits"
    params = {"since": since.isoformat()}

    headers = {"Accept": "application/vnd.github.v3+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"

    response = requests.get(url, params=params, headers=headers, timeout=30)

    if response.status_code == 404:
        print(f"  [SKIP] Repository '{repo}' not found or is private")
        return []
    elif response.status_code == 403:
        print(f"  [SKIP] Rate limited or access denied for '{repo}'")
        return []
    elif response.status_code != 200:
        print(f"  [ERROR] Failed to fetch '{repo}': HTTP {response.status_code}")
        return []

    return response.json()


def format_email_body(all_commits: dict, since: datetime) -> str:
    """Format the email body with commit details."""
    since_str = since.strftime("%Y-%m-%d %H:%M UTC")
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "GitHub Daily Commit Report",
        f"Period: {since_str} to {now_str}",
        "=" * 60,
        "",
    ]

    total_commits = 0
    repos_with_commits = 0

    for repo, commits in all_commits.items():
        if not commits:
            continue

        repos_with_commits += 1
        total_commits += len(commits)
        lines.append(f"📁 {repo} ({len(commits)} new commit{'s' if len(commits) != 1 else ''})")
        lines.append("-" * 40)

        for commit in commits:
            sha = commit["sha"][:7]
            message = commit["commit"]["message"].split("\n")[0]
            author = commit["commit"]["author"]["name"]
            date = commit["commit"]["author"]["date"][:10]
            commit_url = commit["html_url"]

            lines.append(f"  • {sha} {message}")
            lines.append(f"    Author: {author} | Date: {date}")
            lines.append(f"    URL: {commit_url}")
            lines.append("")

        lines.append("")

    if total_commits == 0:
        lines.append("No new commits found in the monitored repositories.")
    else:
        lines.append(
            f"Total: {total_commits} commit{'s' if total_commits != 1 else ''} "
            f"across {repos_with_commits} {'repositories' if repos_with_commits != 1 else 'repository'}"
        )

    return "\n".join(lines)


def send_email(subject: str, body: str) -> None:
    """Send email via SMTP."""
    smtp_server = os.environ["SMTP_SERVER"]
    smtp_port = int(os.environ["SMTP_PORT"])
    smtp_username = os.environ["SMTP_USERNAME"]
    smtp_password = os.environ["SMTP_PASSWORD"]
    recipient = os.environ["EMAIL_RECIPIENT"]

    msg = MIMEMultipart()
    msg["From"] = smtp_username
    msg["To"] = recipient
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, recipient, msg.as_string())

    print(f"Email sent successfully to {recipient}")


def main():
    # Load from .env file first, then override with env vars
    file_config = load_config_from_file()

    # Set env vars from file config if not already set
    for key, value in file_config.items():
        if key not in os.environ:
            os.environ[key] = value

    repos_str = os.environ.get("MONITORED_REPOS", "")
    if not repos_str:
        print("Error: MONITORED_REPOS not found")
        print("Please set it in .env file or as environment variable.")
        return

    repos = [r.strip() for r in repos_str.split(",") if r.strip()]

    if not repos:
        print("Error: No repositories specified in MONITORED_REPOS")
        return

    since = datetime.now(timezone.utc) - timedelta(hours=24)

    print(f"Monitoring {len(repos)} repositories since {since.strftime('%Y-%m-%d %H:%M UTC')}")
    print()

    all_commits = {}

    for repo in repos:
        print(f"Checking {repo}...")
        commits = get_commits_from_repo(repo, since)
        all_commits[repo] = commits
        print(f"  Found {len(commits)} commit{'s' if len(commits) != 1 else ''}")

    print()

    total_commits = sum(len(c) for c in all_commits.values())

    if total_commits == 0:
        print("No new commits found. Skipping email.")
        return

    print(f"Total: {total_commits} commits found. Sending email...")

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    subject = f"[GitHub Monitor] Daily Commit Report - {date_str}"
    body = format_email_body(all_commits, since)

    send_email(subject, body)


if __name__ == "__main__":
    main()
