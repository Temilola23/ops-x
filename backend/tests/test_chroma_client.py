import importlib
import os
from unittest.mock import patch

import numpy as np
import pytest


@pytest.fixture(scope="session")
def chroma_module(tmp_path_factory):
    import_chroma_dir = tmp_path_factory.mktemp("chroma-import")
    with patch.dict(os.environ, {"CHROMA_PERSIST_DIR": str(import_chroma_dir)}):
        return importlib.import_module("integrations.chroma_client")


def test_embedding_has_expected_dimension(chroma_module):
    embedding = chroma_module.generate_embedding("A function that retries failed requests")

    assert len(embedding) == chroma_module.EMBEDDING_DIMENSION == 384
    assert np.isfinite(embedding).all()


def test_search_ranks_semantically_relevant_code_first(chroma_module, tmp_path):
    search = chroma_module.ChromaCodeSearch(persist_directory=str(tmp_path))
    relevant_code = """
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

retry = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session = requests.Session()
session.mount('https://', HTTPAdapter(max_retries=retry))
"""
    irrelevant_code = """
function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
"""

    search.add_code_file(
        "project-1",
        "network/retry.py",
        relevant_code,
        chroma_module.generate_embedding(relevant_code),
    )
    search.add_code_file(
        "project-1",
        "components/counter.tsx",
        irrelevant_code,
        chroma_module.generate_embedding(irrelevant_code),
    )

    results = search.search_code(
        chroma_module.generate_embedding("How does the HTTP client retry errors with exponential backoff?"),
        project_id="project-1",
        n_results=2,
    )

    assert results["metadatas"][0]["file_path"] == "network/retry.py"


def test_reindexing_same_file_updates_existing_record(chroma_module, tmp_path):
    search = chroma_module.ChromaCodeSearch(persist_directory=str(tmp_path))
    old_content = "def fetch_data(): return 'old'"
    new_content = "def fetch_data(): return 'updated'"

    first_id = search.add_code_file(
        "project-1", "client.py", old_content, chroma_module.generate_embedding(old_content)
    )
    second_id = search.add_code_file(
        "project-1", "client.py", new_content, chroma_module.generate_embedding(new_content)
    )

    stored = search.collection.get(ids=[first_id], include=["documents"])
    assert first_id == second_id
    assert search.collection.count() == 1
    assert stored["documents"] == [new_content]


def test_search_isolated_to_requested_project(chroma_module, tmp_path):
    search = chroma_module.ChromaCodeSearch(persist_directory=str(tmp_path))
    content = "def validate_access_token(token): return token.is_valid()"
    embedding = chroma_module.generate_embedding(content)
    search.add_code_file("project-a", "auth.py", content, embedding)
    search.add_code_file("project-b", "auth.py", content, embedding)

    results = search.search_code(embedding, project_id="project-a", n_results=5)

    assert len(results["ids"]) == 1
    assert results["metadatas"][0]["project_id"] == "project-a"


def test_new_collection_does_not_modify_legacy_collection(chroma_module, tmp_path):
    client = chroma_module.chromadb.PersistentClient(path=str(tmp_path))
    legacy = client.get_or_create_collection(name="code_embeddings")
    legacy.add(ids=["legacy-record"], embeddings=[[0.0] * 384], documents=["preserve me"])

    search = chroma_module.ChromaCodeSearch(persist_directory=str(tmp_path))

    assert search.collection.name == "code_embeddings_bge_small_v1"
    assert legacy.get(ids=["legacy-record"], include=["documents"])["documents"] == ["preserve me"]