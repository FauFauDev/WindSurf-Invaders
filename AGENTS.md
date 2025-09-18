# Repository Guidelines

## Project Structure & Module Organization
- `main.py` drives the pygame loop, routes events, and wires HUD/menu screens from `ui/`.
- `entities/` holds player, alien, boss, projectile, explosion, and power-up behaviours; prefer adding gameplay rules here.
- `effects/` and `systems/score.py` manage visual feedback and combo/highscore logic, while shared helpers live in `utils/`.
- `assets/` stores art and audio grouped into `backgrounds/`, `images/`, `sounds/`; `data/` keeps JSON highscores, and `documentation/` contains reference material for features and mechanics.
- Support scripts (`download_assets.py`, `create_effects.py`, `create_sounds.py`) regenerate derived assets after new media or balance tweaks.

## Build, Test, and Development Commands
- `python -m venv venv` then `venv\Scripts\activate` creates an isolated runtime; re-run when switching Python versions.
- `pip install -r requirements.txt` installs `pygame` and logging utilities used across modules.
- `python download_assets.py` fetches missing sprites/audio before first run; rerun if assets fail integrity checks.
- `python create_effects.py` and `python create_sounds.py` rebuild procedural effects so new parameters land in `assets/`.
- `python main.py` launches the game; start sessions with the console visible to catch debug prints from asset loaders.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indents and descriptive `snake_case` for functions; classes stay `PascalCase` (keep existing French names but prefer English for new code).
- Centralize constants in `config.py` using upper-case names, and avoid magic numbers in gameplay loops.
- Favor small, testable helpers inside `utils/` when logic is reused across entities or UI layers.
- Use Python’s `logging` module when adding instrumentation so output continues to stream into `game.log`.

## Testing Guidelines
- There is no automated suite yet; start new coverage with `pytest` under `tests/`, isolating logic that does not touch live `pygame` surfaces.
- Exercise critical flows manually: `python main.py`, trigger waves, toggle fullscreen with `F`, pause/resume with `P`, and confirm highscores persist in `data/highscore.json`.
- Update `documentation/technical_documentation.md` with any systemic changes so QA can mirror scenarios.

## Commit & Pull Request Guidelines
- Match the existing history: concise, present-tense subject lines (e.g., “Add fullscreen toggle handling”) and scoped commits per feature or fix.
- Reference affected modules in the body when context is not obvious, and link issues if applicable.
- PRs should call out gameplay impacts, include before/after screenshots for UI, and note any asset regeneration steps reviewers must repeat.
