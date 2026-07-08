def _auth_headers(client):
    client.post("/api/v1/tenants/", json={"name": "TestCo", "slug": "testco"})
    client.post("/api/v1/auth/register", json={
        "tenant_slug": "testco", "full_name": "Test User",
        "email": "test@testco.com", "password": "testpass123", "role_name": "admin",
    })
    login = client.post("/api/v1/auth/login", json={"email": "test@testco.com", "password": "testpass123"})
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _setup_product_and_warehouse(client, headers):
    p = client.post("/api/v1/products/", json={"sku": "SKU-T1", "name": "TestProd", "base_price": 10, "cost_price": 5}, headers=headers)
    w = client.post("/api/v1/inventory/warehouses", json={"name": "TestWH"}, headers=headers)
    return p.json()["id"], w.json()["id"]


def test_stock_receipt_increases_quantity(client):
    headers = _auth_headers(client)
    product_id, warehouse_id = _setup_product_and_warehouse(client, headers)

    resp = client.post("/api/v1/inventory/stock/adjust", json={
        "product_id": product_id, "warehouse_id": warehouse_id,
        "quantity": 50, "movement_type": "receipt",
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["quantity"] == "50.00" or float(resp.json()["quantity"]) == 50.0


def test_cannot_oversell_stock(client):
    headers = _auth_headers(client)
    product_id, warehouse_id = _setup_product_and_warehouse(client, headers)

    client.post("/api/v1/inventory/stock/adjust", json={
        "product_id": product_id, "warehouse_id": warehouse_id,
        "quantity": 10, "movement_type": "receipt",
    }, headers=headers)

    resp = client.post("/api/v1/inventory/stock/adjust", json={
        "product_id": product_id, "warehouse_id": warehouse_id,
        "quantity": -20, "movement_type": "dispatch",
    }, headers=headers)
    assert resp.status_code == 400


def test_reconciliation_matches_after_movements(client):
    headers = _auth_headers(client)
    product_id, warehouse_id = _setup_product_and_warehouse(client, headers)

    client.post("/api/v1/inventory/stock/adjust", json={
        "product_id": product_id, "warehouse_id": warehouse_id,
        "quantity": 100, "movement_type": "receipt",
    }, headers=headers)
    client.post("/api/v1/inventory/stock/adjust", json={
        "product_id": product_id, "warehouse_id": warehouse_id,
        "quantity": -30, "movement_type": "dispatch",
    }, headers=headers)

    resp = client.get(f"/api/v1/inventory/reconcile?product_id={product_id}&warehouse_id={warehouse_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["is_balanced"] is True
