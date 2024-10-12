# 🤖 Building ReAct Agents from Scratch: A Hands-On Guide with Gemini

This repository provides a comprehensive guide and implementation for creating ReAct (Reasoning and Acting) agents from scratch using Python and leveraging Google's Gemini as the Large Language Model (LLM) of choice.

![ReAct Agent](./img/react-agent.png "ReAct Agent")

## 📚 Contents

- Step-by-step implementation of the ReAct pattern
- Multiple examples showcasing ReAct agents in action
- Optimizations specific to the Gemini model
- Tools integration (Google Search and Wikipedia)

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Git
- Poetry (for dependency management)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/username/react-agents-from-scratch.git
   cd react-agents-from-scratch
   ```

2. Set up a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. Install Poetry (if not already installed):
   ```
   pip install poetry
   ```

4. Install project dependencies:
   ```
   poetry install
   ```

5. Set up environment variables:
   ```
   export PYTHONDONTWRITEBYTECODE=1
   export PYTHONPATH=$PYTHONPATH:.
   ```

### Setting up Credentials

1. Create a `credentials` folder in the project root:
   ```
   mkdir credentials
   ```

2. Set up GCP service account credentials:
   - Go to the Google Cloud Console (https://console.cloud.google.com/).
   - Create a new project or select an existing one.
   - Navigate to "APIs & Services" > "Credentials".
   - Click "Create Credentials" > "Service Account Key".
   - Select your service account, choose JSON as the key type, and click "Create".
   - Save the downloaded JSON file as `key.json` in the `credentials` folder.

3. Set up SERP API credentials:
   - Sign up for a SERP API account at https://serpapi.com/.
   - Obtain your API key from the dashboard.
   - Create a file named `key.yml` in the `credentials` folder.
   - Add your SERP API token in the following format:
     ```yaml
     serp:
       key: your_serp_api_key_here
     ```

Note: The `credentials` folder is included in `.gitignore` to prevent sensitive information from being committed.

## 🛠️ Project Structure

- `src/tools/`: Contains implementations for Google Search (via SERP API) and Wikipedia search.
- `src/react/`: Houses the core ReAct agent implementation.
- `data/input/`: Stores input prompts for the ReAct agent.
- `data/output/`: Contains output traces from example runs.

<p align="center">
    <img src="./img/think_act_observe_loop.png" alt="Think Act Observe Loop" width="50%">
</p>

## 🖥️ Usage

1. Ensure you're in the project root directory with your virtual environment activated.

2. Run the ReAct agent:
   ```
   python src/react/agent.py
   ```

3. The agent uses the prompt from `./data/input/react.txt` and generates output traces in `./data/output/`.

4. To run individual tools:
   - Google Search: `python src/tools/serp.py`
   - Wikipedia Search: `python src/tools/wiki.py`

5. For a non-agentic approach with programmatic routing:
   ```
   python src/tools/manager.py
   ```

## 🤝 Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to submit pull requests, report issues, or request features.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 📚 Further Reading

For a detailed explanation of the ReAct pattern and this implementation, check out our accompanying Medium article: [[Building ReAct Agents from Scratch: A Hands-On Guide using Gemini](https://medium.com/google-cloud/building-react-agents-from-scratch-a-hands-on-guide-using-gemini-ffe4621d90ae)]