# Introduction to Artificial Intelligence 2026/2027

This repository contains the tutoring material for the 2026/2027 Introduction to Artificial Intelligence at University of Studies of Trieste.

The repository is updated on a weekly basis. Lecture notebooks and solutions for previous weeks will be published during the course; solutions are not included yet.

## Structure

```text
root/
├── notebooks/lectures/   # Lecture notebooks and exercises
├── resources/           # VS Code setup guide and screenshots
├── scripts/             # Vacuum World, agents, runner and game assets
├── tests/               # Focused maintenance regression tests
├── pyproject.toml       # Direct dependencies
├── uv.lock              # Locked dependency versions
├── requirements.txt     # Export of the lockfile for pip / VS Code
└── README.md
```

## Quick start with uv and JupyterLab

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), for example with `pip install uv` if you already have Python and pip. Then run:

```bash
git clone https://github.com/frekkoz3/Introduction-to-Artificial-Intelligence-2026-2027.git
cd Introduction-to-Artificial-Intelligence-2026-2027
uv sync --locked
uv run --locked jupyter lab
```

uv creates `.venv` and obtains Python 3.12 if needed. The existing dependency versions support Python 3.12; no dependency downgrade is required. Open a notebook under `notebooks/lectures/` and select **Python 3 (ipykernel)**. The server and kernel run in the project environment. Run the first import cell before the Vacuum World examples; it locates `scripts` from the repository root or a notebook subfolder.

The notebooks contain unfinished exercises: complete the TODOs yourself before running cells that depend on them. Interactive Pygame examples open a separate desktop window, so run them on a machine with a graphical desktop.

## VS Code / traditional installation

The illustrated [VS Code setup guide](resources/setup.md) remains available. Use Python **3.12.x**, create a virtual environment, and install `requirements.txt`. In an activated environment, the equivalent command is:

```bash
python -m pip install -r requirements.txt
```

If you used uv, select the existing `.venv` as your VS Code notebook kernel instead of creating another environment.

## Dependency maintenance and checks

`pyproject.toml` lists direct dependencies; `uv.lock` records the full resolution. After intentionally changing dependencies, regenerate both tracked dependency files together:

```bash
uv lock
uv export --locked --no-hashes --no-emit-project --output-file requirements.txt
```

Do not edit dependency versions in `requirements.txt` separately. See the [uv project guide](https://docs.astral.sh/uv/guides/projects/) for details.

Run the focused headless checks with:

```bash
uv lock --check
uv sync --locked
uv run --locked python -m unittest discover -s tests -v
```

The exact ignore rule for `notebooks/solutions/0_setup.ipynb` protects the previously unpublished solution. Remove that rule when intentionally publishing it; other educational notebooks are not ignored.
