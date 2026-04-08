# Setup Checklist

Use this checklist when you need the shortest path to a working Kognitos app-development environment.

## Baseline

- Confirm `git`, `python3`, `node`, and `npm` are installed.
- Confirm the target repository's package manager and framework.
- Identify the Kognitos environment you are targeting: local, shared dev, staging, or production-adjacent.

## Kognitos-Specific Setup

- Identify the API surface or SDK the application will call.
- Confirm how authentication is established for local development.
- Confirm where workflow/SOP definitions live and who owns them.

## Repository Setup

- Install dependencies.
- Read the root architecture or onboarding docs.
- Verify the application starts locally.
- Verify linting or validation commands can run before editing code.

## Exit Criteria

- The app boots locally or there is a concrete blocker with evidence.
- Required secrets and environment variables are named and documented.
- The engineer knows which skill to use next.
