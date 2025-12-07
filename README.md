# Classmusic: A Data Engineering Learning Journey

## About This Project

`classmusic` is a hands-on project designed to document and facilitate the process of learning data engineering from the ground up. This repository serves as a practical exercise and learning log for building a complete data pipeline, from environment setup to a functional, tested ETL (Extract, Transform, Load) process.

The core idea is to ingest music listening history ("scrobbles") from the **Last.fm API**, apply object-oriented principles to model the data, and build a robust, testable system. The development process is strictly guided by **Test-Driven Development (TDD)** to ensure code quality and a deep understanding of each component.

## Learning Objectives

The main objectives for this project are:

-   **Mastering a TDD Workflow**: Rigorously applying the Red-Green-Refactor cycle for all new features.
-   **Object-Oriented Design**: Moving from procedural scripts to a class-based architecture (`Config`, `LastfmClient`, etc.) to model the problem domain.
-   **API Client Development**: Building a reusable and robust client to interact with the Last.fm external API, including handling pagination and errors.
-   **Reproducible Environments**: Using `pipenv` to manage project dependencies for both development and production.
-   **Code Quality and Automation**: Integrating tools like `black` for auto-formatting to maintain a clean and consistent codebase.

## Project Architecture

The project is organized following a clean architecture approach to separate concerns:

-   `src/`: Contains all the application's source code.
    -   `config/`: Manages configuration loading (e.g., from `.env` files).
    -   `clients/`: Handles communication with external APIs (e.g., `LastfmClient`).
    -   `models/`: (Planned) Will contain the data models for entities like `Track`, `Album`, and `Artist`.
    -   `etl/`: (Planned) Will orchestrate the Extract, Transform, and Load process.
-   `tests/`: Contains all the unit tests, mirroring the `src` directory structure. All tests are written using `pytest` and `unittest.mock`.
-   `docs/`: Contains documentation, learning notes, and architectural decisions made during the project.

## Current Status

-   **Environment**: A reproducible Python 3.12 environment is set up using `pyenv` and `pipenv`.
-   **Configuration**: A `Config` class has been developed via TDD to securely load credentials from a `.env` file.
-   **Last.fm Client**: The `LastfmClient` class is under development.
    -   The core private method `_make_request` has been built and rigorously tested using TDD. It correctly handles successful responses and raises descriptive errors for failed API calls.
    -   The first public method, `get_recenttracks`, has been initiated, and its development is following a TDD process to handle the complexities of the Last.fm API, including pagination.

## Getting Started

### Prerequisites

-   Python 3.12 (preferably managed with `pyenv`)
-   `pipenv`

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/classmusic.git
    cd classmusic
    ```

2.  **Set the local Python version (if using `pyenv`):**
    ```bash
    pyenv local 3.12.0
    ```

3.  **Install project dependencies:**
    This command will create a `.venv` directory in the project folder and install all production and development packages from the `Pipfile.lock`.
    ```bash
    pipenv sync --dev
    ```

4.  **Create the environment file:**
    Create a `.env` file in the root of the project and add your Last.fm API credentials:
    ```
    LASTFM_KEY="your_lastfm_api_key"
    ```

5.  **Activate the virtual environment:**
    ```bash
    pipenv shell
    ```

6.  **Run the tests:**
    Once the environment is active, you can run the test suite to verify that everything is set up correctly.
    ```bash
    pytest
    ```

## Project Guidance

The development process is being guided by an AI assistant. The interactions, goals, and mentorship guidelines are documented in the `GEMINI.md` file.