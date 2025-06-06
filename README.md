# Hello LangGraph

A simple demonstration of building a ReAct agent using LangGraph and Ollama. This project showcases how to create an interactive AI agent that can process user queries and execute tools while providing transparent reasoning steps.

## Features

- 🤖 ReAct Agent implementation using LangGraph
- 🔄 Streaming responses with thought process visibility
- 🛠️ Custom tool integration (weather information demo)
- 🤝 Integration with Ollama for local LLM support

## Prerequisites

- Python 3.13 or higher
- Ollama installed with qwen3:8b model

## Installation

1. Clone the repository
2. Install dependencies with poetry:

```bash
poetry install
```

## Usage

The project contains several demo examples showcasing different aspects of LangGraph capabilities. To run any demo:

```bash
python src/<demo_name>.py
```

Each demo will demonstrate the following features:
- Thought process visualization (🤔)
- Tool calls execution (🔧)
- Tool results display (✅)
- Final responses (💬)
