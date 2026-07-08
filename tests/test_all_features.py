import pytest
from decimal import Decimal

def _register_and_login(client, tenant_slug, email, password, full_name, role_name="admin"):
    # Create tenant
    t_resp = client.post("/api/v1/tenants/", json={"name": tenant_slug.capitalize(), "slug": tenant_slug})
    assert t_resp.status_code == 201, f"Tenant creation failed: {t_resp.status_code} {t_resp.text}"
    # Register user
    r_resp = client.post("/api/v1/auth/register", json={
        "tenant_slug": tenant_slug, "full_name": full_name,
        "email": email, "password": password, "role_name": role_name
    })
    assert r_resp.status_code == 201, f"User registration failed: {r_resp.status_code} {r_resp.text}"
    # Login
    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, f"Login failed: {login.status_code} {login.text}"
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_full_business_flow(client):
    headers = _register_and_login(client, "co1", "user@co1.com", "password123", "Co1 Admin")
    
    # 1. Finance Init
    resp = client.post("/api/v1/finance/accounts/init", headers=headers)
    assert resp.status_code == 200
    
    # 2. Products
    cat_resp = client.post("/api/v1/products/categories", json={"name": "Electronics"}, headers=headers)
    assert cat_resp.status_code == 201
    cat_id = cat_resp.json()["id"]
    
    brand_resp = client.post("/api/v1/products/brands", json={"name": "Sony"}, headers=headers)
    assert brand_resp.status_code == 201
    brand_id = brand_resp.json()["id"]
    
    prod_resp = client.post("/api/v1/products/", json={
        "sku": "SONY-TV-01", "name": "Sony Bravia", "base_price": 500.0, "cost_price": 300.0,
        "category_id": cat_id, "brand_id": brand_id
    }, headers=headers)
    assert prod_resp.status_code == 201
    product_id = prod_resp.json()["id"]
    
    # 3. Warehouses
    wh_resp = client.post("/api/v1/inventory/warehouses", json={"name": "Main WH"}, headers=headers)
    assert wh_resp.status_code == 201
    warehouse_id = wh_resp.json()["id"]
    
    # 4. Vendors
    vendor_resp = client.post("/api/v1/vendors/", json={
        "name": "Sony Corp", "email": "sales@sony.com", "phone": "12345",
        "address": "Tokyo", "payment_terms": "NET30", "compliance_score": 95.0
    }, headers=headers)
    assert vendor_resp.status_code == 201
    vendor_id = vendor_resp.json()["id"]
    
    # 5. Procurement flow
    pr_resp = client.post("/api/v1/procurement/requests", json={
        "product_id": product_id, "quantity": 10.0, "justification": "Restock"
    }, headers=headers)
    assert pr_resp.status_code == 201
    pr_id = pr_resp.json()["id"]
    
    approve_pr_resp = client.post(f"/api/v1/procurement/requests/{pr_id}/approve", headers=headers)
    assert approve_pr_resp.status_code == 200
    
    po_resp = client.post(f"/api/v1/procurement/requests/{pr_id}/convert-to-po", json={
        "vendor_id": vendor_id, "warehouse_id": warehouse_id, "unit_price": 280.00
    }, headers=headers)
    assert po_resp.status_code == 200
    po_id = po_resp.json()["id"]
    
    gr_resp = client.post("/api/v1/procurement/goods-receipt", json={
        "purchase_order_id": po_id, "quantity": 10.0
    }, headers=headers)
    assert gr_resp.status_code == 201
    
    pay_resp = client.post("/api/v1/procurement/vendor-payments", json={
        "purchase_order_id": po_id, "amount": 2800.00
    }, headers=headers)
    assert pay_resp.status_code == 201
    
    # 6. Sales flow
    cust_resp = client.post("/api/v1/crm/customers", json={
        "name": "John Doe", "email": "john@gmail.com", "phone": "555-5555"
    }, headers=headers)
    assert cust_resp.status_code == 201
    customer_id = cust_resp.json()["id"]
    
    so_resp = client.post("/api/v1/sales/orders", json={
        "customer_id": customer_id, "warehouse_id": warehouse_id, "product_id": product_id,
        "quantity": 2.0, "unit_price": 480.0, "discount_percent": 5.0, "tax_percent": 10.0
    }, headers=headers)
    assert so_resp.status_code == 201
    so_id = so_resp.json()["id"]
    
    confirm_so_resp = client.post(f"/api/v1/sales/orders/{so_id}/confirm", headers=headers)
    assert confirm_so_resp.status_code == 200
    
    invoice_resp = client.post(f"/api/v1/sales/orders/{so_id}/invoice", headers=headers)
    assert invoice_resp.status_code == 200
    invoice_id = invoice_resp.json()["id"]
    
    # 7. Order processing & logistics
    ship_resp = client.post("/api/v1/orders/shipments", json={
        "sales_order_id": so_id, "carrier": "FedEx", "tracking_number": "TRACK123"
    }, headers=headers)
    assert ship_resp.status_code == 201
    shipment_id = ship_resp.json()["id"]
    
    mark_ship_resp = client.post(f"/api/v1/orders/shipments/{shipment_id}/mark-shipped", headers=headers)
    assert mark_ship_resp.status_code == 200
    
    history_resp = client.get(f"/api/v1/orders/status-history/{so_id}", headers=headers)
    assert history_resp.status_code == 200
    
    ret_resp = client.post("/api/v1/orders/returns", json={
        "sales_order_id": so_id, "reason": "Defective item", "quantity": 1.0
    }, headers=headers)
    assert ret_resp.status_code == 201
    return_request_id = ret_resp.json()["id"]
    
    ref_resp = client.post("/api/v1/orders/refunds", json={
        "return_request_id": return_request_id, "amount": 240.0
    }, headers=headers)
    assert ref_resp.status_code == 201
    
    # 8. Reports & Dashboard
    sales_rep = client.get("/api/v1/reports/sales", headers=headers)
    assert sales_rep.status_code == 200
    
    csv_rep = client.get("/api/v1/reports/sales/export.csv", headers=headers)
    assert csv_rep.status_code == 200
    
    dash_exec = client.get("/api/v1/reports/dashboard/executive", headers=headers)
    assert dash_exec.status_code == 200
    
    dash_fore = client.get("/api/v1/reports/dashboard/forecast", headers=headers)
    assert dash_fore.status_code == 200

def test_workflow_and_gateway(client):
    headers = _register_and_login(client, "co2", "user@co2.com", "password123", "Co2 Admin")
    
    # Workflow Approval Request
    wf_resp = client.post("/api/v1/workflow/approvals?entity_type=SalesOrder&entity_id=42&approver_role=admin&sla_hours=12", headers=headers)
    assert wf_resp.status_code == 200
    approval_id = wf_resp.json()["id"]
    
    decide_resp = client.post(f"/api/v1/workflow/approvals/{approval_id}/decide?approve=true", headers=headers)
    assert decide_resp.status_code == 200
    
    # Gateway Webhooks
    wh_resp = client.post("/api/v1/gateway/webhooks?event_type=order_confirmed&target_url=https://webhook.site/test", headers=headers)
    assert wh_resp.status_code == 200
    
    whs_resp = client.get("/api/v1/gateway/webhooks", headers=headers)
    assert whs_resp.status_code == 200
    assert len(whs_resp.json()) == 1

def test_monitoring_endpoints(client):
    # Detailed health
    dh = client.get("/api/v1/monitoring/health-detailed")
    assert dh.status_code == 200
    assert dh.json()["status"] == "healthy"
    
    # Metrics
    m = client.get("/api/v1/monitoring/metrics")
    assert m.status_code == 200
    # Note: currently returns 0. Later we can verify if it logs requests.

def test_multi_tenant_isolation(client):
    headers_tenant1 = _register_and_login(client, "tenant1", "admin@tenant1.com", "password123", "Tenant 1 Admin")
    headers_tenant2 = _register_and_login(client, "tenant2", "admin@tenant2.com", "password123", "Tenant 2 Admin")

    # 1. Product SKU isolation
    p1 = client.post("/api/v1/products/", json={
        "sku": "COMMON-SKU", "name": "Prod 1", "base_price": 100.0, "cost_price": 50.0
    }, headers=headers_tenant1)
    assert p1.status_code == 201

    p2 = client.post("/api/v1/products/", json={
        "sku": "COMMON-SKU", "name": "Prod 2", "base_price": 120.0, "cost_price": 60.0
    }, headers=headers_tenant2)
    
    # Under a correct multi-tenant system, this should succeed because they are in different tenants!
    # Let's check what it returns
    assert p2.status_code == 201, f"Tenant 2 failed to create product with same SKU: {p2.status_code} {p2.text}"
