# Security Policy

## 🛡️ Supported Versions

We provide security patches and updates for the following versions of deStale:

| Version | Supported          |
| :------ | :----------------- |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

---

## 🔒 Reporting a Vulnerability

If you discover a security vulnerability or potential prompt injection vulnerability in deStale, please do NOT file a public issue on GitHub.

Instead, please send a detailed security report to:
`security@destale.dev` (or via private GitHub Vulnerability Reporting).

Please include:
1. Type of vulnerability (e.g., prompt injection, credential exposure, API SSRF, unvalidated redirect).
2. Steps to reproduce the issue with sample payload.
3. Potential impact on the verification pipeline or host system.
4. Proposed mitigation or patch if available.

We will acknowledge receipt within 48 hours and work with you on a responsible disclosure timeline.

---

## ⚠️ API Key & Secret Safety

- **Never commit `.env` or real API keys to version control.**
- Always use `.env.example` as a template.
- deStale utilizes `.gitignore` to block `.env`, `*.env`, and `.env.local` files automatically.
- Live internet queries pass through sanitization filters in `utils.py` to prevent prompt injection and model extraction attacks.
