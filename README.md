# FORMETR

FORMETR is a Telegram fitness-planning bot built with Python, aiogram, SQLAlchemy and SQLite. It guides a user through an onboarding survey, calculates nutrition targets, creates rule-based training and meal plans, tracks measurements and supports paid access through Telegram Stars.

This is an independent portfolio project developed with substantial AI assistance. It is not presented as commercial client work and does not replace medical advice.

## Features

- step-by-step FSM onboarding and profile reset;
- Mifflin-St Jeor energy calculation, TDEE and macronutrient targets;
- safety rules for minors and medical-risk answers;
- deterministic training plans and exercise substitutions;
- food catalogue, portion calculation and daily or weekly meal plans;
- body-measurement history and multi-week progress reviews;
- goal changes while preserving historical plans;
- seven-day trial and recurring FORMETR Pro access through Telegram Stars;
- administrator commands for permanent complimentary access;
- versioned database schema with Alembic migrations.

## Verification status

- 29 automated tests pass;
- the Telegram token and bot identity were verified during the private deployment audit;
- the local database is on Alembic migration `0004`;
- a final Telegram Stars purchase must be tested by the owner before accepting real payments;
- production hosting is not included in this repository.

## Technology

Python 3.12+, aiogram 3, SQLAlchemy 2, aiosqlite, Alembic, pydantic-settings, pytest and pytest-asyncio.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .[dev]
Copy-Item .env.example .env
alembic upgrade head
python -m app
```

Add a BotFather token to `.env` before starting the bot. Never commit `.env`, the runtime database or log files.

## Test

```powershell
pytest -q
```

The manual Telegram checklist is in [`docs/manual-test.md`](docs/manual-test.md).

## Docker

```bash
docker build -t formetr .
docker run --env-file .env -v formetr-data:/data formetr
```

The container stores SQLite data in `/data/formetr.db`. A production host must attach a persistent volume to `/data`.

## Production checklist

1. Use a new production BotFather token and keep it in the host's secret store.
2. Set `DATABASE_URL=sqlite+aiosqlite:////data/formetr.db` and attach persistent storage.
3. Set `SUPPORT_CONTACT` to a monitored account or email.
4. Review the Russian privacy notice and terms in `docs/`.
5. Run the manual checklist with a separate Telegram test account.
6. Make a controlled Telegram Stars purchase and verify activation and expiration.
7. Configure process restarts and database backups.

## Structure

- `app/bot` - handlers, FSM states, middleware and keyboards;
- `app/calculations` - deterministic formulas and safety rules;
- `app/services` - plans, subscriptions and progress reviews;
- `app/database` - SQLAlchemy models and repositories;
- `app/exercises` and `app/food` - local catalogues;
- `alembic` - database migrations;
- `tests` - automated domain and integration tests.

## Limitations

FORMETR does not diagnose conditions, prescribe treatment or promise local fat loss. Production operation still requires hosting, monitoring, backups and a real-payment smoke test.
