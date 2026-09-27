import pytest
from Api import app, db

app.config["TESTING"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

@pytest.fixture(autouse=True)
def setup_database():
    with app.app_context():
        db.create_all()

        yield

        db.session.remove()
        db.drop_all()
def test_get_assets():
    client = app.test_client()

    response = client.get("/assets")

    assert response.status_code == 200

def test_create_asset_without_api_key():
    client = app.test_client()

    response = client.post("/assets", json={
        "asset_name": "Dell Latitude",
        "asset_type": "Laptop",
        "status": "Active"
    })

    assert response.status_code == 401

def test_create_asset_with_api_key():
    client = app.test_client()

    response = client.post(
        "/assets",
        headers={"X-API-Key": "changeme123"},
        json={
            "asset_name": "ThinkPad",
            "asset_type": "Laptop",
            "status": "Active"
        }
    )

    assert response.status_code == 201

def test_invalid_status():
    client = app.test_client()

    response = client.post(
        "/assets",
        headers={"X-API-Key": "changeme123"},
        json={
            "asset_name": "Dell Latitude",
            "asset_type": "Laptop",
            "status": "Flying"
        }
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == \
        "Invalid status. Use Active, In Repair, or Retired"

def test_update_asset():
    client = app.test_client()

    # First create an asset
    create_response = client.post(
        "/assets",
        headers={"X-API-Key": "changeme123"},
        json={
            "asset_name": "MacBook Pro",
            "asset_type": "Laptop",
            "status": "Active"
        }
    )

    asset_id = create_response.get_json()["id"]

    # Then update it
    response = client.put(
        f"/assets/{asset_id}",
        headers={"X-API-Key": "changeme123"},
        json={
            "asset_name": "MacBook Pro",
            "asset_type": "Laptop",
            "status": "In Repair"
        }
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "In Repair"

def test_delete_asset():
    client = app.test_client()

    # Create an asset first
    create_response = client.post(
        "/assets",
        headers={"X-API-Key": "changeme123"},
        json={
            "asset_name": "Dell Desktop",
            "asset_type": "Desktop",
            "status": "Active"
        }
    )

    asset_id = create_response.get_json()["id"]

    # Delete the asset
    response = client.delete(
        f"/assets/{asset_id}",
        headers={"X-API-Key": "changeme123"}
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Asset deleted successfully"

    # Make sure it is actually gone
    check_response = client.get(f"/assets/{asset_id}")

    assert check_response.status_code == 404

def test_asset_not_found():
    client = app.test_client()

    response = client.get("/assets/9999")

    assert response.status_code == 404