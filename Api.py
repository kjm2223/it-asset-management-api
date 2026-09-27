from flask import Flask, jsonify, request 
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("API_KEY")
print("API key loaded:", key is not None)

def is_key():
    received_key = request.headers.get("X-API-Key")

    print("Header received:", received_key is not None)
    print("Keys match:", received_key == key)

    return received_key == key

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///assets.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_name = db.Column(db.String(100), nullable=False)
    asset_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)

primary_key=True

ASSETS = [
    {
        "id": 1,
        "asset_name": "Dell Latitude 5540",
        "asset_type": "Laptop",
        "status": "Active"
    },
    {
        "id": 2,
        "asset_name": "HP ProDesk 600",
        "asset_type": "Desktop",
        "status": "In Repair"
    }
]


@app.get('/assets')
def get_assets():
    assets = Asset.query.all()

    return jsonify([
        {
            "id": asset.id,
            "asset_name": asset.asset_name,
            "asset_type": asset.asset_type,
            "status": asset.status
        }
        for asset in assets
    ])


@app.get('/assets/<int:asset_id>')
def get_asset(asset_id):
    asset = db.get_or_404(Asset, asset_id)

    return jsonify({
        "id": asset.id,
        "asset_name": asset.asset_name,
        "asset_type": asset.asset_type,
        "status": asset.status
    })

def validate_asset(data):
    if not data:
        return "Request body is required"

    required_fields = ["asset_name", "asset_type", "status"]

    for field in required_fields:
        if field not in data:
            return f"{field} is required"

        if not isinstance(data[field], str) or not data[field].strip():
            return f"{field} cannot be empty"

    valid_statuses = ["Active", "In Repair", "Retired"]

    if data["status"] not in valid_statuses:
        return "Invalid status. Use Active, In Repair, or Retired"

    return None

@app.post('/assets')
def create_asset():
    if not is_key():
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    
    error = validate_asset(data)
    
    if error:
        return jsonify({"error": error}), 400

    new_asset = Asset(
        asset_name=data["asset_name"],
        asset_type=data["asset_type"],
        status=data["status"]
    )

    db.session.add(new_asset)
    db.session.commit()

    return jsonify({
        "id": new_asset.id,
        "asset_name": new_asset.asset_name,
        "asset_type": new_asset.asset_type,
        "status": new_asset.status
    }), 201



@app.put('/assets/<int:asset_id>')
def update_asset(asset_id):
    if not is_key():
            return jsonify({"error": "Unauthorized"}), 401
    asset = db.get_or_404(Asset, asset_id)

    data = request.get_json()

    error = validate_asset(data)

    if error:
        return jsonify({"error": error}), 400

    asset.asset_name = data["asset_name"]
    asset.asset_type = data["asset_type"]
    asset.status = data["status"]

    db.session.commit()

    return jsonify({
        "id": asset.id,
        "asset_name": asset.asset_name,
        "asset_type": asset.asset_type,
        "status": asset.status
    })
@app.delete('/assets/<int:asset_id>')
def delete_asset(asset_id):
    if not is_key():
            return jsonify({"error": "Unauthorized"}), 401
    asset = db.get_or_404(Asset, asset_id)

    db.session.delete(asset)
    db.session.commit()

    return jsonify({
        "message": "Asset deleted successfully"
    })



    return jsonify({"error": "Asset not found"}), 404



with app.app_context():
    db.create_all()



if __name__ == "__main__":
    app.run(host="127.0.0.1",port=3000)