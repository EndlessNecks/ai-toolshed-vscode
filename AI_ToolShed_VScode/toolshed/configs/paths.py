import os

# Root of the tool’s code inside the VSIX
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Qdrant local folder, NOT Chroma
VECTOR_INDEX_PATH = os.path.join(PROJECT_ROOT, "vector_db", "qdrant")

# Where chunker pulls documents/code from
DOCS_ROOT = os.path.join(PROJECT_ROOT, "workspace")
