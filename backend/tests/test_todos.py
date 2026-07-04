def test_create_todo(client, auth_headers):
    response = client.post(
        "/api/v1/todos",
        headers=auth_headers,
        json={"title": "测试待办", "priority": 1},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "测试待办"


def test_list_todos(client, auth_headers):
    client.post(
        "/api/v1/todos",
        headers=auth_headers,
        json={"title": "待办1", "priority": 1},
    )
    response = client.get("/api/v1/todos", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_toggle_todo(client, auth_headers):
    resp = client.post(
        "/api/v1/todos",
        headers=auth_headers,
        json={"title": "切换测试", "priority": 0},
    )
    todo_id = resp.json()["id"]

    update_resp = client.put(
        f"/api/v1/todos/{todo_id}",
        headers=auth_headers,
        json={"completed": True},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["completed"] is True
