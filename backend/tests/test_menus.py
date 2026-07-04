def test_get_menus(client, auth_headers):
    response = client.get("/api/v1/menus", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
