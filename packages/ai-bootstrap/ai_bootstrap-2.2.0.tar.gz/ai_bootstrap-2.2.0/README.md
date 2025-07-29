# AI Bootstrap 🚀

**Your AI-Powered Project Scaffolding CLI**

AI Bootstrap is a professional CLI tool that uses AI to plan, scaffold, and generate production-ready AI/ML project blueprints. Go from a simple idea to a fully structured, modern Python application in seconds.

[![PyPI Version](https://img.shields.io/pypi/v/ai-bootstrap.svg)](https://pypi.org/project/ai-bootstrap/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/your-username/ai-bootstrap/main.yml?branch=main)](https://github.com/your-username/ai-bootstrap/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/ai-bootstrap.svg)](https://pypi.org/project/ai-bootstrap/)

---

AI Bootstrap streamlines the initial, often tedious, phases of AI project development. Whether you prefer an AI-driven chat to plan your project or a guided interactive setup, this tool creates a robust foundation with modern best practices, allowing you to focus on building unique features.

## ✨ Key Features

-   **🤖 AI-Powered Planning**: Describe your project in plain English and let the AI Planner select the best blueprint, frameworks, and structure for you.
-   **💬 Interactive & Chat-Based Creation**: Choose between a guided interactive CLI that walks you through every option or an AI-driven chat for a "just tell me what you want" experience.
-   **🏗️ Multiple Project Blueprints**:
    -   **RAG System**: End-to-end Retrieval-Augmented Generation.
    -   **Multi-Agent System**: Sophisticated agentic workflows with LangGraph.
    -   **Multimodal Chatbot**: Chat with text, images, and audio.
    -   **Core LangChain Application**: A modular starting point for any LangChain project.
-   **🔌 Flexible Integrations**:
    -   **LLM Providers**: OpenAI, Anthropic, Ollama, Mistral.
    -   **Frameworks**: LangChain, LlamaIndex, LangGraph.
    -   **Vector Stores**: Chroma, FAISS.
    -   **UI Frameworks**: Streamlit, Chainlit, FastAPI, Flask, CLI.
-   **📦 Modern Python Stack**:
    -   Type-safe configuration with Pydantic.
    -   Easy environment management with `.env` files.
    -   Includes scaffolding for `pytest` and Jupyter notebooks.
    -   Automatic `requirements.txt` and `README.md` generation for each project.
-   **🔄 Project Updating**: Keep your projects current with the `ai-bootstrap update` command, which seamlessly pulls in the latest template improvements.

---

## 📋 Prerequisites

Before you begin, ensure you have the following:

-   **Python 3.9+**
-   An API key for your chosen LLM provider: [OpenAI](https://platform.openai.com/), [Anthropic](https://www.anthropic.com/), or [Mistral](https://mistral.ai/).
-   **(Optional)** [Ollama](https://ollama.com/) for running local LLMs.
-   **(Optional)** [Docker](https://www.docker.com/) & VS Code [Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers) for a sandboxed development environment.

---

## 🛠️ Installation

Install the tool directly from PyPI:

```sh
pip install ai-bootstrap
```

---

## 🎉 Getting Started

Creating your first production-ready AI application is just a few commands away.

### 1. Set Up Your API Keys

Create a `.env` file in your working directory to store your API keys. The tool will automatically load them.

```ini
# .env file
OPENAI_API_KEY="sk-..."
# ANTHROPIC_API_KEY="sk-..."
# MISTRAL_API_KEY="..."
# TAVILY_API_KEY="..." # Optional, for web search tools
```

### 2. Create Your First Project (AI-Powered)

This is the recommended and fastest way to get started. Use the `--chat` flag to let the AI Planner configure your project.

```sh
ai-bootstrap create --chat
```

The tool will prompt you for a short description. For example:

> **"I want to build a chatbot that can answer questions about multiple PDF documents using a web interface."**

The AI Planner will analyze this, generate a project plan, ask for your confirmation, and then scaffold the entire project.

### 3. Create a Project (Interactive Mode)

If you prefer to make every decision yourself, run the command without any flags.

```sh
ai-bootstrap create
```

This will launch a guided interactive prompt that walks you through selecting a blueprint, UI framework, LLM provider, and other options.

---

## 📚 Core Commands

Here is a summary of the available commands. For a detailed view, run `ai-bootstrap --help`.

| Command                   | Description                                                                 | Example                                                               |
| ------------------------- | --------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `create`                  | Create a new AI project using either interactive or AI-driven modes.        | `ai-bootstrap create --chat`                                          |
| `update`                  | Update an existing project with the latest template changes.                | `ai-bootstrap update` (run inside project dir)                        |
| `list-blueprints`         | Display a table of all available project blueprints and their features.     | `ai-bootstrap list-blueprints`                                        |
| `test-ai-planner`         | Test the AI Planner with a project description without creating files.      | `ai-bootstrap test-ai-planner --description "A multi-agent researcher"` |
| `help-table`              | Show a detailed table of all CLI commands and their arguments.              | `ai-bootstrap help-table`                                             |

---

## 🗂️ Project Blueprints

AI Bootstrap provides several battle-tested blueprints for common AI application patterns.

1.  **RAG System (`rag`)**
    -   **Description**: A complete Retrieval-Augmented Generation system for question-answering over your documents.
    -   **Tech**: LangChain/LlamaIndex, Chroma/FAISS, Streamlit/Chainlit/FastAPI/CLI.

2.  **Multi-Agent System (`multi-agent`)**
    -   **Description**: An advanced system with multiple AI agents collaborating to solve complex tasks, orchestrated by LangGraph.
    -   **Tech**: LangGraph, Supervisor Pattern, State Management, In-memory/Redis/Postgres memory.

3.  **Multimodal Chatbot (`multimodal-chatbot`)**
    -   **Description**: A chatbot capable of processing and responding with text, images, and audio.
    -   **Tech**: Chainlit/Streamlit/Flask UI, OpenAI/Anthropic multimodal models.

4.  **Core LangChain Application (`core-langchain`)**
    -   **Description**: A modular and scalable foundation for building custom LangChain applications.
    -   **Tech**: Custom Chains, Prompt Management, Tool Integration, Streamlit/FastAPI/CLI.

---

## 📝 Roadmap & Future Plans

This project is under active development. Here are some of the features planned for upcoming releases:

#### Template Enhancements
-   More advanced agent workflows and memory options in multi-agent systems.
-   Additional vector store integrations (e.g., Pinecone, Weaviate).
-   Enhanced Docker and deployment templates for all blueprints.
-   More robust test and notebook scaffolding.

#### CLI & Application Features
-   Project validation and linting before generation.
-   Support for custom, user-defined blueprints.
-   Richer AI Planner explanations and reasoning in the CLI.
-   Automatic virtual environment creation and `.env` population.

---

## 🤝 Contributing

Contributions are welcome! If you have ideas for new features, blueprints, or improvements, please open an issue or submit a pull request on our GitHub repository.

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
