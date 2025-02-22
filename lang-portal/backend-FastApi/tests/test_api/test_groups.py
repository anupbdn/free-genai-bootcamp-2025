def test_create_group(client):
    group_data = {
        "name": "Test Group"
    }
    response = client.post("/api/groups", json=group_data)
    assert response.status_code == 200
    assert response.json()["name"] == group_data["name"]

def test_get_groups(client):
    response = client.get("/api/groups")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_group_words(client):
    # Create a group
    group_data = {"name": "Test Group"}
    group_response = client.post("/api/groups", json=group_data)
    group_id = group_response.json()["id"]

    # Get words in group
    response = client.get(f"/api/groups/{group_id}/words")
    assert response.status_code == 200
    assert isinstance(response.json(), list) 