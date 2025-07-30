# AGENTS

**Project**: `jupyterlab-resource-tracker`
**Type**: JupyterLab Extension (Server + Frontend)

This document provides a quick reference of the main agents/components of the project,
listing their location, technologies, and responsibilities.

---

## Backend (Server Extension)

- **Location**: `jupyterlab_resource_tracker/`
- **Language**: Python 3.x
- **Framework**: Jupyter Server Extension (based on Tornado)
- **Responsibilities**:
  - Define HTTP API routes and handlers.
  - Retrieve and process logs from AWS S3.
  - Expose usage and cost data in JSON format.
- **Key modules**:
  - `handlers.py`: route setup and example handler (`RouteHandler`).
  - `logs_handler.py`: logs handler (`LogsHandler`) and Pydantic models (`Summary`, `Detail`).

## Frontend (Labextension)

- **Location**: `src/`
- **Language**: TypeScript / JavaScript
- **Framework/UI**: React, Material-UI (MUI), JupyterLab-specific APIs
- **Responsibilities**:
  - Consume the backend REST API.
  - Render dashboards, tables, and charts for usage and cost data.
  - Manage user interactions and visualization in JupyterLab.
- **Build & Development**:
  - Commands: `jlpm build`, `jlpm watch` (alternatively `yarn` / `npm`).
  - Unit tests: Jest (`jlpm test`).

## Integration & End-to-End (E2E) Tests

- **Location**: `ui-tests/`
- **Tool**: Playwright + Galata (JupyterLab helper)
- **Description**: End-to-end tests for the extension within JupyterLab.

## Test Structure

- **Backend** (pytest): `jupyterlab_resource_tracker/tests/`
- **Frontend** (jest): `.spec.ts` / `.spec.js` in `src/`, configured via `jest.config.js`
- **Integration** (ui-tests): `ui-tests/` with guide in `ui-tests/README.md`

## Packaging & Distribution

- **Backend**: packaged via `setup.py` / `pyproject.toml`
- **Frontend**: npm package inside `jupyterlab_resource_tracker/labextension/`
- **Wheel & sdist**: generated in `dist/` (`.whl` / `.tar.gz`)

## Additional Resources

- Read [`README.md`](README.md) for installation, development, and troubleshooting guidance.
- See [`RELEASE.md`](RELEASE.md) for details on the release process.