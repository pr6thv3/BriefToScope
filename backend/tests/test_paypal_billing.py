import os

os.environ["DEMO_MODE"] = "True"
os.environ["SUPABASE_URL"] = "http://localhost:54321"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "mock_key"

from fastapi.testclient import TestClient

from app.config import get_settings

get_settings.cache_clear()

from app.main import app

client = TestClient(app)


def test_paypal_subscription_webhook_reconciles_once():
    event = {
        "id": "WH-PAYPAL-ACTIVE-1",
        "event_type": "BILLING.SUBSCRIPTION.ACTIVATED",
        "resource": {
            "id": "I-BRIEFTOSCOPE-1",
            "plan_id": "P-SOLO",
            "custom_id": "org_demo",
            "status": "ACTIVE",
            "subscriber": {"payer_id": "PAYER-DEMO"},
        },
    }

    first = client.post("/webhooks/paypal", json=event)
    assert first.status_code == 200
    assert first.json()["status"] == "processed"
    assert first.json()["billing_event"] == "subscription_synced"

    duplicate = client.post("/webhooks/paypal", json=event)
    assert duplicate.status_code == 200
    assert duplicate.json()["status"] == "ignored"
