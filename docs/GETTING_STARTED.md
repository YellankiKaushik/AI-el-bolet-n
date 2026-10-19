# Getting started on Windows

Run Signal Daily on your own laptop, draft with a local model, and review in your browser. You do not need Docker, a VPS, a domain or an email account for this workflow. No public newsletter service is deployed by cloning the repository.

## 1. Install and verify prerequisites

Install Python from [python.org](https://www.python.org/downloads/windows/), Git from [Git for Windows](https://git-scm.com/downloads/win), and Ollama from its [official Windows download](https://ollama.com/download/windows). Use Python 3.11 or 3.12 for the CI-tested combinations. Other Python 3.11+ versions may work but are not covered by the matrix. Follow the installer instructions, then open a new PowerShell window so its PATH is refreshed. The application itself has no npm/frontend build dependencies.

```powershell
git --version
py -3 --version
ollama --version
```

If `py` is missing, try `python --version`. If that opens the Store or reports no runtime, use the actual installed executable or fix the installation using the official installer. Do not assume a PATH alias is a working interpreter. [Troubleshooting Python](TROUBLESHOOTING.md#python-not-found).

Ollama needs enough memory/disk for the model you choose. Model size and performance vary; this project does not automatically install weights or promise a hardware minimum. Start with an already installed local tag where possible.

## 2. Get the source

```powershell
git clone https://github.com/YellankiKaushik/AI-el-bolet-n.git
Set-Location AI-el-bolet-n
```

The cloned directory is the application root: `run.py`, `server.py` and `README.md` should be immediately inside it. There is no extra nested `signal-daily` directory in a fresh clone.

Optional developer virtual environment (local use does not require pip packages):

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe tools/setup_local.py
```

Using the executable directly avoids a PowerShell activation-policy change. To make the launcher prefer this environment:

```powershell
$env:SIGNAL_DAILY_PYTHON=(Resolve-Path .venv\Scripts\python.exe).Path
```

## 3. Create private configuration

Without a virtual environment, use:

```powershell
py -3 tools/setup_local.py
```

Setup exclusively creates `.env` from `.env.example`, with random administrator/session secrets and email disabled. Existing configuration is preserved. Open `.env` in your local editor; never paste its contents into an issue or commit it. Windows permissions are inherited from the project folder, so keep that folder restricted to your account. The password is the value of `ADMIN_PASSWORD`; the application has no username.

Keep these non-secret local settings:

```dotenv
APP_ENV=development
HOST=127.0.0.1
PORT=8787
PUBLIC_URL=http://localhost:8787
OLLAMA_URL=http://127.0.0.1:11434
OLLAMA_MODEL=gemma4:e4b
ENABLE_LOCAL_GENERATION=true
EMAIL_DELIVERY_ENABLED=false
```

Keep your generated secrets, not example labels. `DATABASE_PATH=data/signal_daily.db` is private, relative to the project root. Startup creates/migrates it automatically; do not delete it to troubleshoot. [All configuration options](CONFIGURATION.md).

## 4. Start Ollama and select a local model

Open the installed Ollama application, then inspect its actual inventory:

```powershell
ollama list
Invoke-RestMethod http://127.0.0.1:11434/api/tags | Select-Object -ExpandProperty models | Select-Object name
```

Put an exact installed tag in `.env`. `gemma4:e4b` is the verified development model. Use a local tag, not `:cloud`. If no suitable model is installed and you deliberately choose to download its weights:

```powershell
ollama pull gemma4:e4b
```

This can be a substantial download; the application never runs it automatically. Ollama's [model catalog](https://ollama.com/library/gemma4/tags) and [Windows guide](https://docs.ollama.com/windows) describe the current installation/model behavior. If the service is not already listening, `ollama serve` in another terminal can start it. Do not launch a duplicate server if the endpoint already responds. Keep its bind address on loopback; no tunnel or router forwarding is needed.

## 5. Start Signal Daily

```powershell
.\Start-Local.ps1
```

The Windows launcher checks Python, creates config only if missing, and forces loopback development mode, port 8787, local generation enabled and real email off. It leaves your existing `.env` untouched. Keep the terminal open while using the browser.

If PowerShell refuses `.ps1` execution, use the working interpreter directly instead of weakening security policy:

```powershell
$env:HOST='127.0.0.1'
$env:PORT='8787'
$env:APP_ENV='development'
$env:PUBLIC_URL='http://localhost:8787'
$env:EMAIL_DELIVERY_ENABLED='false'
$env:ENABLE_LOCAL_GENERATION='true'
py -3 run.py
```

Replace `py -3` with `python` or the full executable path if that is your working Python. For the original development laptop only, the already installed fallback was:

```powershell
$SignalPython=Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $SignalPython run.py
```

That path is not a dependency for other users. Check a full executable's version before using it.

## 6. Open and log in

- Reader homepage: [http://localhost:8787](http://localhost:8787)
- Editor: [http://localhost:8787/admin](http://localhost:8787/admin)
- Health check: [http://localhost:8787/health](http://localhost:8787/health)

Enter your existing `ADMIN_PASSWORD` privately and choose **Unlock workbench**. Empty homepage/archive pages are expected until you deliberately publish an edition. To prepare a draft, follow [the first newsletter walkthrough](USER_GUIDE.md#prepare-your-first-edition).

## 7. Stop and restart without losing work

Press Ctrl+C in the server terminal. Start it again from the same checkout with `Start-Local.ps1` or the direct interpreter command. The same SQLite file retains drafts, history and consent; restarting invalidates old editor sessions, so log in again. Avoid a second instance against the same database; an OS process lock rejects it.

If an earlier automated session started the app in the background, identify the exact loopback listener using `Get-NetTCPConnection -LocalPort 8787 -State Listen` and inspect that process before stopping it. Do not blindly kill all Python processes or use a stale PID from an old report.

Before upgrades, take a consistent backup:

```powershell
py -3 tools/database_backup.py backup data/signal_daily.db backups/before-upgrade-UNIQUE-NAME.db
py -3 tools/database_backup.py check backups/before-upgrade-UNIQUE-NAME.db
```

Replace `UNIQUE-NAME`; overwrites are intentionally refused. Backups contain private data, so restrict/encrypt them. [Recovery details](PRODUCTION_RUNBOOK.md#backups-restoration-and-daily-operations).

## A safe practice workspace

```powershell
py -3 tools/demo.py
```

Open [http://127.0.0.1:8789/admin](http://127.0.0.1:8789/admin). Its private demo password is in `.tmp/demo/credentials.json`. It uses a different database, explicit demo banner and fictional fixtures; SMTP and model generation are disabled. Restarting preserves demo edits. It never reads your real `.env` or resets the real newsletter database. Follow [manual testing](LOCAL_TESTING_GUIDE.md) for a fresh empty acceptance workspace.

For common problems—port conflicts, timeouts, source failures, login and empty archives—use [TROUBLESHOOTING.md](TROUBLESHOOTING.md). Public hosting and live email are separate setup projects, not required installation steps.
