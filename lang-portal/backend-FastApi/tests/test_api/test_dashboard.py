def test_get_dashboard_stats(client):
    response = client.get("/api/dashboard/quick-stats")
    assert response.status_code == 200
    data = response.json()
    assert "success_rate" in data
    assert "total_study_sessions" in data
    assert "total_active_groups" in data

def test_get_study_progress(client):
    response = client.get("/api/dashboard/study_progress")
    assert response.status_code == 200
    data = response.json()
    assert "total_words_studied" in data
    assert "total_available_words" in data 