# My first LLM project
## View my report here: https://docs.google.com/document/d/1dHaRRZ75O1e_vkmDgR618treAUfdDkI89V5GJ30SWgY/edit?usp=sharing

Made for an AI class assignment.

This simple chatbot app uses a RAG architecture to retrieve relavent information about recent smartphone models from designer websites. This allows the chatbot to give accurate, helpful information in response to user questions about these recent smartphones.

Uses `langchain` libraries and integrations for document, agent, and model management; `chromadb` for embedding vector storage; and `beautifulsoup4` for HTML parsing.

## Running the app
Clone this repo, then navigate to its main directory.

Ensure Python 3.11 is installed (https://www.python.org/downloads/).

This is required because recent versions of Python do not work with core Pydantic V1 functionality (see a related GitHub issue [here](https://github.com/chroma-core/chroma/issues/5996)).
### Create a Python 3.11 virtual environment:
```bash
python3.11 -m venv .venv
```

### Activate the virtual environment:
MacOS/Linux:
```bash
source .venv/bin/activate
```

Windows:
```
.venv\Scripts\activate
```

### Install required modules using `pip`:
```bash
pip install langchain langchain-community langchain-openai langchain-chroma beautifulsoup4
```

### Run the chatbot:
```bash
python main.py
```

If the `OPEN_AI_API_KEY` environment variable is not set, you will be prompted to paste in your API key when the program starts.
