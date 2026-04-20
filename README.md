# Repository Agent: Codebase RAG Multi-Agent System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

An multi-agent system designed for intelligent codebase interaction, analysis, and modification. This project integrates retrieval-augmented generation (RAG) techniques with specialized AI agents to provide an interface for developers to understand and evolve their codebases.

---

## Architecture

The system is composed of several key components working in harmony:

-   **Agent Orchestrator**: Built with Google ADK, it manages the workflow between specialized agents (Retrieval, Refinement, Classifier, and Specialists).
-   **Repository API**: A high-performance search service powered by **Qdrant** and **Tree-sitter**, implementing hybrid indexing (UniXcoder for code logic and all-MiniLM for natural language).
-   **Frontend**: A modern, responsive dashboard built with **TanStack Start**, **React**, and **Tailwind CSS**.
-   **Benchmarking Suite**: A dedicated system to evaluate agent performance and visualize results.

---

## Features

-   **Hybrid Code Search**: Find code using natural language or structural code queries.
-   **Multi-Agent RAG**: Intelligent context retrieval and task routing.
-   **Performance Visualization**: Interactive charts for benchmarking agent accuracy and speed.
-   **Extensible Parser**: Support for Python, JavaScript, TypeScript, and C# out of the box, with an easy path to add more languages via Tree-sitter.
-   **Docker Ready**: Fully containerized for consistent development and deployment.

---

## Project Structure

```text
.
├── agent/                  # Core AI agent logic (ADK-based)
├── frontend/               # TanStack Start web application
├── repository_api/         # Qdrant-backed code search service
├── memvid_api_server/      # Alternative indexing service (Memvid) (not in use)
├── docker-compose.yaml     # Service orchestration
└── .env.example            # Environment configuration template
```

---

## Getting Started

### Prerequisites

-   [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
-   Python 3.10+
-   Node.js & npm

### Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/nevernorbo/repository-agent.git
    cd repository-agent
    ```

2.  **Configure Environment:**
    Copy `.env.example` to `.env` and fill in the required keys (Google API Key, Qdrant URL, etc.).
    ```bash
    cp .env.example .env
    ```

3.  **Launch with Docker:**
    ```bash
    docker-compose up --build
    ```

The services will be available at:
-   **Frontend**: `http://localhost:3000`
-   **Repository API**: `http://localhost:8000`
-   **Agent API**: `http://localhost:8100`

---

## Benchmarking

The project includes two benchmarking suites to evaluate different components of the system:

### Indexing Benchmarks
Located in `repository_api/benchmarks`, these tests evaluate the accuracy and performance of the code search and retrieval system.

To run:
1. Navigate to `repository_api/benchmarks`.
2. Run `python run_benchmarks.py --all`.

### Agent Benchmarks
Located in `agent/benchmarks`, these tests evaluate the quality and reliability of the AI agent's responses and task execution.

To run:
1. Navigate to `agent/benchmarks`.
2. Run `python run_benchmark.py`.

---

## Adding Language Support

To add a new programming language to the search index:
1.  Add the language definition in `repository_api/code_search/index/language_definitions.py`.
2.  Implement the language-specific parsing logic in `repository_api/code_search/index/parser_common.py`.
3.  Re-index your repositories.
