# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅        |

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security-sensitive reports.

Email or DM the maintainer via GitHub: [@BruceLanLan](https://github.com/BruceLanLan)

Include:

- Description of the issue
- Steps to reproduce
- Impact assessment (if known)
- Suggested fix (optional)

We aim to acknowledge reports within 7 days.

## Operational security for users

- Never commit `.env` or API keys
- Restrict CORS and reverse-proxy auth before exposing the FastAPI server to the internet
- Treat generated reports as untrusted content (prompt injection via web pages is possible)
- Prefer read-only / sandboxed environments when enabling shell tools in Deep Agents
