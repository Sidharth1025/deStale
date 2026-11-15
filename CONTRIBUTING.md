# Contributing to deStale

Thank you for your interest in contributing to **deStale**! We welcome contributions to improve our live AI freshness and fact-checking engine.

---

## 🛠️ Development Workflow

### 1. Fork and Clone
1. Fork the repository to your GitHub account.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/<your-username>/deStale.git
   cd deStale
   ```

### 2. Environment Setup
Create and activate an isolated virtual environment:
```bash
python -m venv venv

# On Linux/macOS
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

Install production and testing dependencies:
```bash
pip install -r requirements.txt
pip install pytest pytest-cov flake8 black
```

### 3. Configure Local Credentials
Copy the example environment template:
```bash
cp .env.example .env
```
Fill in your local Bifrost AI Gateway URL or Tavily Search API key. If you do not have active API credentials, you can set `DEMO_MODE=true` to test locally with pre-cached ground-truth audits.

---

## 🧪 Running Tests & Quality Checks

Before submitting a Pull Request, ensure all tests pass:
```bash
pytest -v tests/
```

Check code style and linting:
```bash
flake8 . --count --max-line-length=120
```

---

## 🌿 Branching & Commit Guidelines

- **Branch naming convention:**
  - `feat/feature-name` (e.g., `feat/add-brave-search-provider`)
  - `fix/bug-fix` (e.g., `fix/bifrost-timeout-handling`)
  - `docs/doc-updates` (e.g., `docs/update-architecture-flow`)

- **Commit message conventions:**
  - `feat: add fallback search provider for Tavily`
  - `fix: resolve JSON parsing issue in claim_extractor`
  - `test: add unit tests for domain authority scorer`
  - `docs: update presentation slides and viva questions`

---

## 📬 Submitting a Pull Request (PR)

1. Push your branch to your forked repository:
   ```bash
   git push origin feat/your-feature-name
   ```
2. Open a Pull Request on GitHub against the `main` branch.
3. Describe the change clearly in the PR description, referencing any relevant issues.
4. Ensure CI tests pass on all supported Python versions (3.10, 3.11, 3.12).
