# GitHub Daily Commit Monitor

A GitHub Action that monitors public repositories for new commits and sends a daily email summary at 8:00 UTC.

## Features

- Monitors multiple public repositories for new commits
- Sends daily email reports via SMTP (Gmail, Outlook, etc.)
- Only sends email when there are new commits (no spam)
- Includes full commit details: SHA, message, author, date, and URL
- Manual trigger support via GitHub Actions UI

## Setup

### 1. Fork or Clone This Repository

### 2. Configure GitHub Secrets

Go to your repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add the following secrets:

| Secret | Description | Example |
|--------|-------------|---------|
| `MONITORED_REPOS` | Comma-separated list of repos to monitor | `facebook/react,vuejs/vue,angular/angular` |
| `SMTP_SERVER` | SMTP server address | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USERNAME` | Your email address | `you@gmail.com` |
| `SMTP_PASSWORD` | App password (not your main password) | `abcd-efgh-ijkl-mnop` |
| `EMAIL_RECIPIENT` | Where to send the report | `you@gmail.com` |

### 3. Gmail Setup (if using Gmail)

1. Enable 2-Factor Authentication on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate an app password for "Mail"
4. Use that 16-character password as `SMTP_PASSWORD`

### 4. Outlook Setup (if using Outlook)

1. Go to https://account.microsoft.com/security
2. Select "Advanced security options"
3. Under "App passwords", select "Create a new app password"
4. Use that password as `SMTP_PASSWORD`

**SMTP Settings for Outlook:**
- Server: `smtp-mail.outlook.com`
- Port: `587`

## How to Use

### Automatic (Daily)

The action runs automatically at **8:00 UTC every day**. If there are new commits in the last 24 hours, you'll receive an email.

### Manual Trigger

1. Go to **Actions** → **Daily Commit Monitor**
2. Click **Run workflow**

## Monitored Repositories Format

Use `owner/repo` format, comma-separated:

```
facebook/react, vuejs/vue, sveltejs/svelte, tailwindlabs/tailwindcss
```

## Email Example

```
GitHub Daily Commit Report
Period: 2026-06-23 08:00 UTC to 2026-06-24 08:00 UTC
============================================================

📁 facebook/react (3 new commits)
----------------------------------------
  • abc1234 feat: add new concurrent mode feature
    Author: John Doe | Date: 2026-06-23
    URL: https://github.com/facebook/react/commit/abc1234

  • def5678 fix: resolve memory leak in useEffect
    Author: Jane Smith | Date: 2026-06-23
    URL: https://github.com/facebook/react/commit/def5678

  • ghi9012 docs: update documentation for hooks
    Author: Bob Wilson | Date: 2026-06-23
    URL: https://github.com/facebook/react/commit/ghi9012

📁 vuejs/vue (1 new commit)
----------------------------------------
  • jkl3456 refactor: improve template compilation speed
    Author: Alice Chen | Date: 2026-06-23
    URL: https://github.com/vuejs/vue/commit/jkl3456

Total: 4 commits across 2 repositories
```

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── commit-monitor.yml    # GitHub Action workflow
├── scripts/
│   └── commit_monitor.py         # Main monitoring script
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Troubleshooting

### "No new commits found. Skipping email."

This means none of the monitored repositories had commits in the last 24 hours. This is normal behavior.

### "Repository not found or is private"

The repository name might be misspelled, or it might be a private repository. This action only works with public repositories.

### "Rate limited or access denied"

GitHub API has rate limits. For unauthenticated requests: 60/hour. For authenticated requests: 5,000/hour. The action uses the built-in `GITHUB_TOKEN` for authentication.

### Email not received

1. Check your spam folder
2. Verify all SMTP secrets are correct
3. Make sure you're using an app password (not your main password)

## License

MIT
