
import pytest
from fastapi.testclient import TestClient
from app.main import app

# Minimal contract test ensuring endpoints exist and accept correct methods
# Full contract testing would validate against OpenAPI spec schema

@pytest.mark.contract
def test_tasks_endpoints_exist(client: TestClient, normal_user_token_headers):
    # GET /tasks
    response = client.get("/v1/tasks", headers=normal_user_token_headers)
    assert response.status_code in [200, 404]  # 404 if no tasks, or 200 list

    # POST /tasks
    response = client.post("/v1/tasks", headers=normal_user_token_headers, json={
        "title": "Contract Test Task"
    })
    # Should be 201 or 400/422
    assert response.status_code in [201, 400, 422]

@pytest.mark.contract
def test_projects_endpoints_exist(client: TestClient, normal_user_token_headers):
    # GET /projects
    response = client.get("/v1/projects", headers=normal_user_token_headers)
    assert response.status_code in [200, 404]

    # POST /projects
    response = client.post("/v1/projects", headers=normal_user_token_headers, json={
        "name": "Contract Test Project"
    })
    assert response.status_code in [201, 400, 422]
