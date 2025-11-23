---
description: Deploy Sage Bot to GitHub
---

# Deploy to GitHub Workflow

This workflow deploys the Sage Bot project to the GitHub repository at https://github.com/sree27691/Sage.git

## Prerequisites

- Git repository initialized
- Remote 'origin' configured with GitHub URL
- Personal Access Token configured (if using HTTPS)

## Deployment Steps

### 1. Check Git Status

```bash
git status
```

Review any uncommitted changes.

### 2. Add All Changes

// turbo
```bash
git add .
```

### 3. Commit Changes

Provide a descriptive commit message:

```bash
git commit -m "Your commit message here"
```

**Example commit messages**:
- `feat: Add new conflict detection feature`
- `fix: Resolve Trust Card data isolation issue`
- `docs: Update README with setup instructions`
- `refactor: Improve LLM client error handling`

### 4. Push to GitHub

// turbo
```bash
git push origin main
```

## Quick Deploy (One Command)

If you want to quickly commit and push all changes:

```bash
git add . && git commit -m "Update: $(date +%Y-%m-%d)" && git push origin main
```

## Troubleshooting

### Authentication Issues

If you get a 403 error, update the remote URL with your Personal Access Token:

```bash
git remote set-url origin https://YOUR_TOKEN@github.com/sree27691/Sage.git
```

### Merge Conflicts

If there are conflicts:

```bash
git pull origin main --rebase
# Resolve conflicts
git add .
git rebase --continue
git push origin main
```

### View Remote Configuration

```bash
git remote -v
```

## Post-Deployment

After successful deployment:
1. Visit https://github.com/sree27691/Sage to verify changes
2. Check GitHub Actions (if configured) for CI/CD status
3. Review the commit history

## Notes

- Always review changes with `git status` before committing
- Use meaningful commit messages following conventional commits format
- Pull latest changes before starting work: `git pull origin main`
