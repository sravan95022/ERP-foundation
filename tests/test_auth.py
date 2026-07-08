def _create_tenant_and_user(client):
    client.post("/api/v1/tenants/", json={"name": "TestCo", "slug": "testco"})
    client.post("/api/v1/auth/register", json={
        "tenant_slug": "testco", "full_name": "Test User",
        "email": "test@testco.com", "password": "testpass123", "role_name": "admin",
    })


def test_register_and_login(client):
    _create_tenant_and_user(client)
    resp = client.post("/api/v1/auth/login", json={"email": "test@testco.com", "password": "testpass123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password_fails(client):
    _create_tenant_and_user(client)
    resp = client.post("/api/v1/auth/login", json={"email": "test@testco.com", "password": "wrongpass"})
    assert resp.status_code == 401


def test_duplicate_tenant_slug_rejected(client):
    client.post("/api/v1/tenants/", json={"name": "TestCo", "slug": "testco"})
    resp = client.post("/api/v1/tenants/", json={"name": "TestCo2", "slug": "testco"})
    assert resp.status_code == 400


def test_protected_route_requires_token(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_me_returns_correct_user(client):
    _create_tenant_and_user(client)
    login = client.post("/api/v1/auth/login", json={"email": "test@testco.com", "password": "testpass123"})
    token = login.json()["access_token"]
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@testco.com"
