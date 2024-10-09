# 🤖 Building ReAct Agents from Scratch: A Hands-On Guide

This repository provides a comprehensive collection of examples demonstrating the effective implementation of the ReAct (Reasoning and Acting) pattern in Large Language Model (LLM) prompting. It includes various implementations and optimizations of agents leveraging the ReAct pattern, with a focus on the Gemini model.

## 📚 Contents

- Multiple examples of ReAct pattern implementations
- Variations of ReAct-based agents
- Optimizations specific to the Gemini model

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Git
- Poetry

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/username/react-agents-from-scratch.git
   cd react-agents-from-scratch
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv .react-from-scratch
   source .react-from-scratch/bin/activate  # On Windows, use `.react-from-scratch\Scripts\activate`
   ```

3. Install Poetry if you haven't already:
   ```
   pip install poetry
   ```

4. Install project dependencies using Poetry:
   ```
   poetry install
   ```
   This command will read the `pyproject.toml` file and install all required dependencies.

5. Set up environment variables:
   ```
   export PYTHONDONTWRITEBYTECODE=1
   export PYTHONPATH=$PYTHONPATH:.
   ```

### Setting up Credentials

1. Create a `credentials` folder in the root of the project:
   ```
   mkdir credentials
   ```

2. Add your GCP service account credentials:
   - Create a file named `key.json` in the `credentials` folder.
   - Paste your GCP service account credentials into this file.

3. Set up SERP API credentials:
   - Create a file named `key.yml` in the `credentials` folder.
   - Add your SERP API token to this file in the following format:
     ```yaml
     serp_api_token: your_serp_api_token_here
     ```

## 🛠️ Usage

To use the ReAct agents:

1. Ensure you're in the project's root directory and your virtual environment is activated.

2. Run the desired example script:
   ```
   python examples/example_script.py
   ```

[Add more specific usage instructions for your implemented agents here]

## 🤝 Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to submit pull requests, report issues, or request features.

## 📄 License

This project is licensed under the [MIT License](LICENSE).