from datetime import date


def test_create_record(client, auth_headers):
    response = client.post(
        "/api/v1/records",
        headers=auth_headers,
        json={
            "record_date": "2024-01-15",
            "type": "expense",
            "category": "餐饮",
            "sub_category": "午餐",
            "amount": 35.5,
            "account": "微信",
            "note": "公司楼下",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["category"] == "餐饮"
    assert data["amount"] == 35.5


def test_list_records(client, auth_headers):
    for i in range(5):
        client.post(
            "/api/v1/records",
            headers=auth_headers,
            json={
                "record_date": f"2024-01-{10+i}",
                "type": "expense" if i % 2 == 0 else "income",
                "category": "餐饮" if i % 2 == 0 else "工资",
                "amount": 100 + i,
            },
        )
    response = client.get("/api/v1/records", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 5


def test_summary(client, auth_headers):
    response = client.get("/api/v1/records/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "income" in data
    assert "expense" in data
    assert "balance" in data
    assert "categories" in data


def test_update_record(client, auth_headers):
    create_resp = client.post(
        "/api/v1/records",
        headers=auth_headers,
        json={
            "record_date": "2024-01-15",
            "type": "expense",
            "category": "餐饮",
            "amount": 50,
        },
    )
    record_id = create_resp.json()["id"]

    update_resp = client.put(
        f"/api/v1/records/{record_id}",
        headers=auth_headers,
        json={
            "record_date": "2024-01-16",
            "type": "expense",
            "category": "交通",
            "amount": 20,
        },
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["category"] == "交通"


def test_delete_record(client, auth_headers):
    create_resp = client.post(
        "/api/v1/records",
        headers=auth_headers,
        json={
            "record_date": "2024-01-15",
            "type": "expense",
            "category": "餐饮",
            "amount": 50,
        },
    )
    record_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/api/v1/records/{record_id}", headers=auth_headers)
    assert delete_resp.status_code == 200
