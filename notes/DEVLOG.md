## Changes Made
- Resolved merge conflicts in src/denario_app/app.py and src/denario_app/components.py by preferring upstream changes.
- Added src/denario_app/__init__.py to ensure package importability for tests.
- Updated pyproject.toml to add setuptools build metadata.

## Test Results
- Test run attempted in conda env 'cmbagent'.
- Import error resolved for package discovery; subsequent pip install hit PyMuPDF build error (C++20 toolchain missing).

## Rationale
- Followed @Cursor Rules and AGENTS.md guidance to keep minimal diffs and ensure reproducibility.

## Follow-ups / Open Questions
- Install system toolchain supporting C++20 or pin PyMuPDF to a prebuilt wheel version to avoid source build (e.g., platform-available wheel). Alternatively add constraints to avoid heavy extras during tests.
