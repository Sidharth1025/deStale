# Publish deStale to GitHub

## 1. Create the GitHub repository

On GitHub, create a new repository named `deStale` (or another name you prefer). Choose **Public** if you want it visible on your profile. Do not initialize it with a README, license, or `.gitignore` because this project already contains those files.

## 2. Open a terminal in this project folder

Make sure the terminal's current directory is the folder containing `app.py`, `README.md`, and `requirements.txt`.

## 3. Configure your local environment

Copy `.env.example` to `.env` and enter your own credentials. Never upload `.env`.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS / Linux:

```bash
cp .env.example .env
```

## 4. Initialize Git and push

Replace `YOUR-USERNAME` with your GitHub username and use the exact repository URL shown by GitHub.

```bash
git init
git add .
git status
git commit -m "Initial commit: deStale AI stale-answer detector"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/deStale.git
git push -u origin main
```

Before committing, inspect `git status`. Confirm that `.env` is **not** listed.

## 5. If this folder is already a Git repository

Do not run `git init` again. Check the current remote:

```bash
git remote -v
```

If `origin` is already correct, use:

```bash
git add .
git status
git commit -m "Update deStale project"
git push
```

If `origin` exists but points to the wrong repository, update it:

```bash
git remote set-url origin https://github.com/YOUR-USERNAME/deStale.git
git push -u origin main
```

## 6. Run the project locally

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Then:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit (normally `http://localhost:8501`).

## 7. Run tests

```bash
pytest -q
```

The repository's tests are designed to run without consuming live API credits.

## Common Git errors

- `remote origin already exists`: use `git remote set-url origin ...` rather than adding it again.
- `src refspec main does not match any`: make the first commit, then run `git branch -M main`.
- Authentication failed: authenticate using GitHub's browser sign-in / Git Credential Manager, or configure an approved SSH key. GitHub account passwords are not accepted for HTTPS Git pushes.
- Rejected push because GitHub has a README commit: pull and reconcile the remote first, or recreate an empty repository if it has no valuable content.
