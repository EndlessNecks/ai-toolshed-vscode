\# 🛠️ AI Tool Shed  

\### Local RAG • Codestral • ChromaDB • VS Code (Continue) Integration  



Give your AI full, live access to your codebase.



<div align="center">



!\[GitHub last commit](https://img.shields.io/github/last-commit/yourname/AI\_ToolShed?color=blue)

!\[GitHub issues](https://img.shields.io/github/issues/yourname/AI\_ToolShed)

!\[License](https://img.shields.io/badge/license-MIT-green.svg)

!\[PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

!\[Python Version](https://img.shields.io/badge/python-3.10%2B-yellow.svg)



</div>



---



\# 📚 Overview



The \*\*AI Tool Shed\*\* is a modular, open-source framework that gives an LLM (such as Codestral) \*\*true visibility into your entire codebase\*\*, allowing it to:



\- read your project  

\- retrieve relevant files on demand  

\- suggest changes with accurate file/line references  

\- automatically rebuild its own vector knowledge base on save  

\- integrate seamlessly with \*\*Continue\*\* inside \*\*VS Code\*\*  



Think of it as your own \*\*local GitHub Copilot Enterprise\*\*, but fully under your control.



---



\# 🔧 Core Features



\- ✔️ Local RAG engine (chunk → embed → index → retrieve)

\- ✔️ Persistent ChromaDB vector store

\- ✔️ Watchdog-powered live reindexing

\- ✔️ Continue (VS Code) two-way communication

\- ✔️ Codestral orchestration system

\- ✔️ OpenAI-compatible API client

\- ✔️ Modular, extensible architecture

\- ✔️ Fully open-source \& privacy-friendly



---



\# 🏗️ Architecture



&nbsp;     ┌────────────────────┐

&nbsp;     │     VS Code        │

&nbsp;     │    (Continue)      │

&nbsp;     └─────────┬──────────┘

&nbsp;               │ model\_config

&nbsp;               ▼

&nbsp;   ┌─────────────────────────────┐

&nbsp;   │  codestral\_binding.py       │

&nbsp;   └─────────┬───────────────────┘

&nbsp;             │ creates

&nbsp;             ▼

&nbsp;┌──────────────────────────────┐

&nbsp;│  Codestral Orchestrator      │

&nbsp;│  • builds prompts            │

&nbsp;│  • injects RAG context       │

&nbsp;│  • handles system directives │

&nbsp;└────────────┬─────────────────┘

&nbsp;             │ calls

&nbsp;             ▼

&nbsp;   ┌────────────────────────┐

&nbsp;   │       Retriever        │

&nbsp;   │  • query embeddings    │

&nbsp;   │  • Chroma similarity   │

&nbsp;   └────────────┬───────────┘

&nbsp;                │ reads/writes

&nbsp;   ┌────────────────────────────────┐

&nbsp;   │      Chroma Vector Store       │

&nbsp;   └────────────────────────────────┘

&nbsp;                ▲

&nbsp;                │ writes

&nbsp;   ┌────────────────────────────────┐

&nbsp;   │           Indexer              │

&nbsp;   │       (rerun on save)          │

&nbsp;   └────────────────────────────────┘



---



\# 📁 Project Structure



AI\_ToolShed/

│

├── configs/

│ ├── paths.json

│ ├── rag\_config.json

│

├── rag\_engine/

│ ├── chunker.py

│ ├── embedder.py

│ ├── indexer.py

│ ├── retriever.py

│

├── vector\_db/

│ └── chroma/

│

├── glue\_continue/

│ ├── codestral\_binding.py

│ ├── vscode\_hooks.py

│

├── orchestration/

│ ├── codestral\_client.py

│ ├── codestral\_orchestrator.py

│

├── project\_watchers/

│ ├── watcher.py

│

├── logs/

│

├── tests/

│ ├── test\_embedding.py

│ ├── test\_retrieval.py

│

├── setup.bat

├── requirements.txt

└── README.md



---



\# 🚀 Setup Instructions  

\*(Python 3.14 is the required version)\*



\## 1. Install dependencies



\### Windows

```bash

py -3.14 -m pip install -r requirements.txt


Linux / macOS



Ensure Python 3.14 is installed (via pyenv, source build, etc.):



python3.14 -m pip install -r requirements.txt


2\. Build the initial RAG index

python3.14 rag\_engine/indexer.py


3. Start the auto-index watcher

python3.14 project\_watchers/watcher.py





Automatically rebuilds your vector store whenever you save files.

4. Configure Continue (VS Code)



Add to your Continue config.yaml:



models:

&nbsp; - id: codestral

&nbsp;   provider: openai

&nbsp;   api\_base: "http://localhost:11434/v1"

&nbsp;   model: "codestral-latest"

&nbsp;   api\_key: ""

&nbsp;   max\_tokens: 4096

&nbsp;   temperature: 0.2



python:

&nbsp; scripts:

&nbsp;   onModelLoad: "D:/AI\_Workspace/AI\_ToolShed/glue\_continue/vscode\_hooks.py:on\_model\_loaded"

&nbsp;   onUserMessage: "D:/AI\_Workspace/AI\_ToolShed/glue\_continue/vscode\_hooks.py:handle\_user\_query"



🤖 Usage (Inside VS Code)



Ask Continue:



"Explain how X works"

"Where is Y implemented?"

"Refactor Z for clarity"

"Find API calls to function foo()"





The pipeline:



Retrieves relevant code



Injects it into the system prompt



Sends it to Codestral



Returns a structured answer with file + line references



🧪 Testing

python3.14 -m unittest discover -s tests





Tests include:



test\_embedding.py — embedding normalization \& structure



test\_retrieval.py — uses a temporary in-memory Chroma instance



🔧 Developer Scripts



Rebuild index:



python3.14 rag\_engine/indexer.py





Clear logs:



rm logs/\*.log        # Linux

del logs\\\*.log       # Windows





Start watcher:



python3.14 project\_watchers/watcher.py



📦 Dependencies

chromadb

watchdog

numpy

tqdm

requests





Compatible with any model served over an OpenAI-compatible API (local or remote).

