import importlib
import io
import os
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient


class DisposableProjectQuery:
    def filter(self, _condition):
        return self

    def first(self):
        return SimpleNamespace(id=987654321)


class DisposableProjectDatabase:
    def query(self, _model):
        return DisposableProjectQuery()


def test_semantic_search_api_indexes_and_ranks_authentication_file(tmp_path):
    test_environment = {
        "CHROMA_PERSIST_DIR": str(tmp_path / "import-chroma"),
        "DATABASE_URL": f"sqlite:///{tmp_path / 'unused-test-db.sqlite3'}",
    }
    with patch.dict(os.environ, test_environment):
        chroma_module = importlib.import_module("integrations.chroma_client")
        with redirect_stdout(io.StringIO()):
            projects_module = importlib.import_module("api.projects")

    projects_module.chroma_search = chroma_module.ChromaCodeSearch(
        persist_directory=str(tmp_path / "api-chroma")
    )
    app = FastAPI()
    app.include_router(projects_module.router, prefix="/api")
    app.dependency_overrides[projects_module.get_db] = DisposableProjectDatabase

    authentication_code = """
def authenticate_user(username, password):
    user = users.find_one({"username": username})
    if user is None or not verify_password(password, user.password_hash):
        raise AuthenticationError("Invalid username or password")
    return create_access_token(user.id)
"""
    payment_code = """
def calculate_total(items, tax_rate, discount=0):
    subtotal = sum(item.price * item.quantity for item in items)
    return (subtotal - discount) * (1 + tax_rate)
"""

    with TestClient(app) as client:
        index_response = client.post(
            "/api/projects/987654321/codebase",
            json={
                "auth/login.py": authentication_code,
                "billing/payments.py": payment_code,
            },
        )
        search_response = client.post(
            "/api/projects/987654321/search/semantic",
            params={"query": "Where is user authentication handled?", "n_results": 2},
        )

    assert index_response.status_code == 200
    index_body = index_response.json()
    assert index_body == {
        "success": True,
        "data": {
            "project_id": 987654321,
            "file_count": 2,
            "files": ["auth/login.py", "billing/payments.py"],
        },
        "error": None,
    }

    assert search_response.status_code == 200
    search_body = search_response.json()
    assert search_body["success"] is True
    assert search_body["error"] is None
    assert search_body["data"]["query"] == "Where is user authentication handled?"
    assert search_body["data"]["powered_by"] == "Chroma DB"
    assert len(search_body["data"]["results"]) == 2

    top_result, second_result = search_body["data"]["results"]
    assert top_result["file_path"] == "auth/login.py"
    assert top_result["language"] == "python"
    assert "authenticate_user" in top_result["snippet"]
    assert top_result["relevance_score"] > second_result["relevance_score"]
    assert second_result["file_path"] == "billing/payments.py"
    assert set(top_result) == {"file_path", "snippet", "language", "relevance_score"}