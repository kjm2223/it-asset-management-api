# Import Flask to create the web application.
# jsonify converts Python dictionaries/lists into JSON responses.
# request lets us access information sent by the client, such as JSON and headers.
from flask import Flask, jsonify, request

# Import SQLAlchemy so Flask can communicate with our SQLite database.
from flask_sqlalchemy import SQLAlchemy

# Imports load_dotenv so we can load variables from our .env file.
from dotenv import load_dotenv

# Imports os so we can access environment variables.
import os


# Load the variables stored inside the .env file.
load_dotenv()

# Get the API_KEY value from the .env file.
key = os.getenv("API_KEY")

# Check whether the API key was successfully loaded.
# This prints True or False instead of printing the actual secret key.
print("API key loaded:", key is not None)


# Function used to check if the user sent the correct API key.
def is_key():

    # Get the API key sent in the X-API-Key HTTP header.
    received_key = request.headers.get("X-API-Key")

    # Check whether an API key header was actually received.
    print("Header received:", received_key is not None)

    # Check whether the received API key matches our stored API key.
    print("Keys match:", received_key == key)

    # Returns True if the keys match and False if they do not.
    return received_key == key


# Create the Flask application.
app = Flask(__name__)

# Tell Flask/SQLAlchemy to use a SQLite database named assets.db.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///assets.db"

# Disable SQLAlchemy modification tracking because we don't need it.
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# Connect SQLAlchemy to our Flask application.
db = SQLAlchemy(app)


# Create the Asset database model.
# This represents the Asset table inside our database.
class Asset(db.Model):

    # Create the ID column.
    # Integer means it stores whole numbers.
    # primary_key=True means every asset has a unique ID.
    id = db.Column(db.Integer, primary_key=True)

    # Create the asset_name column.
    # It stores text up to 100 characters.
    # nullable=False means this value is required.
    asset_name = db.Column(db.String(100), nullable=False)

    # Create the asset_type column.
    asset_type = db.Column(db.String(50), nullable=False)

    # Create the status column.
    status = db.Column(db.String(50), nullable=False)


# This line currently does not do anything useful.
# primary_key=True belongs inside the database column definition above.
primary_key=True


# This is a Python list containing sample asset dictionaries.
# NOTE: Your API currently uses the database instead of this ASSETS list.
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


# Create a GET endpoint for /assets.
# This endpoint returns every asset in the database.
@app.get('/assets')
def get_assets():

    # Query the Asset table and retrieve all assets.
    assets = Asset.query.all()

    # Convert all Asset objects into JSON and send them to the client.
    return jsonify([
        {
            "id": asset.id,
            "asset_name": asset.asset_name,
            "asset_type": asset.asset_type,
            "status": asset.status
        }

        # Repeat the dictionary above for every asset in the database.
        for asset in assets
    ])


# Create a GET endpoint for one specific asset.
# Example: GET /assets/1
@app.get('/assets/<int:asset_id>')
def get_asset(asset_id):

    # Search the database for the asset with this ID.
    # If it doesn't exist, Flask automatically returns a 404 error.
    asset = db.get_or_404(Asset, asset_id)

    # Return the asset as JSON.
    return jsonify({
        "id": asset.id,
        "asset_name": asset.asset_name,
        "asset_type": asset.asset_type,
        "status": asset.status
    })


# Function used to validate asset data before creating/updating an asset.
def validate_asset(data):

    # Make sure the request actually contains data.
    if not data:
        return "Request body is required"

    # These fields must exist in every asset request.
    required_fields = ["asset_name", "asset_type", "status"]

    # Loop through each required field.
    for field in required_fields:

        # Check whether the field exists in the JSON.
        if field not in data:
            return f"{field} is required"

        # Make sure the field contains a non-empty string.
        if not isinstance(data[field], str) or not data[field].strip():
            return f"{field} cannot be empty"

    # These are the only statuses that the API accepts.
    valid_statuses = ["Active", "In Repair", "Retired"]

    # Check whether the status sent by the user is allowed.
    if data["status"] not in valid_statuses:
        return "Invalid status. Use Active, In Repair, or Retired"

    # None means no validation errors were found.
    return None


# Create a POST endpoint for adding a new asset.
@app.post('/assets')
def create_asset():

    # Check the API key before allowing the user to create an asset.
    if not is_key():

        # Return HTTP 401 if the API key is incorrect or missing.
        return jsonify({"error": "Unauthorized"}), 401

    # Get the JSON data sent in the request body.
    data = request.get_json()

    # Validate the JSON data.
    error = validate_asset(data)

    # If validation returned an error, send a 400 Bad Request response.
    if error:
        return jsonify({"error": error}), 400

    # Create a new Asset object using the data from the request.
    new_asset = Asset(
        asset_name=data["asset_name"],
        asset_type=data["asset_type"],
        status=data["status"]
    )

    # Add the new asset to the current database session.
    db.session.add(new_asset)

    # Save the new asset permanently to the database.
    db.session.commit()

    # Return the newly created asset as JSON.
    # 201 means "Created."
    return jsonify({
        "id": new_asset.id,
        "asset_name": new_asset.asset_name,
        "asset_type": new_asset.asset_type,
        "status": new_asset.status
    }), 201


# Create a PUT endpoint for updating an existing asset.
# Example: PUT /assets/1
@app.put('/assets/<int:asset_id>')
def update_asset(asset_id):

    # Make sure the user provided the correct API key.
    if not is_key():
        return jsonify({"error": "Unauthorized"}), 401

    # Find the asset using its ID.
    # Automatically returns 404 if it doesn't exist.
    asset = db.get_or_404(Asset, asset_id)

    # Get the new JSON data from the request.
    data = request.get_json()

    # Validate the new asset data.
    error = validate_asset(data)

    # Return a 400 error if the data is invalid.
    if error:
        return jsonify({"error": error}), 400

    # Replace the asset's current name with the new name.
    asset.asset_name = data["asset_name"]

    # Replace the asset's current type with the new type.
    asset.asset_type = data["asset_type"]

    # Replace the asset's current status with the new status.
    asset.status = data["status"]

    # Save the changes to the database.
    db.session.commit()

    # Return the updated asset.
    return jsonify({
        "id": asset.id,
        "asset_name": asset.asset_name,
        "asset_type": asset.asset_type,
        "status": asset.status
    })


# Create a DELETE endpoint for deleting an asset.
# Example: DELETE /assets/1
@app.delete('/assets/<int:asset_id>')
def delete_asset(asset_id):

    # Make sure the correct API key was provided.
    if not is_key():
        return jsonify({"error": "Unauthorized"}), 401

    # Find the asset in the database.
    # Automatically returns 404 if the asset doesn't exist.
    asset = db.get_or_404(Asset, asset_id)

    # Mark the asset to be deleted from the database.
    db.session.delete(asset)

    # Save the deletion.
    db.session.commit()

    # Tell the client that the asset was successfully deleted.
    return jsonify({
        "message": "Asset deleted successfully"
    })


    # NOTE:
    # This code will never run because there is already a return above.
    return jsonify({"error": "Asset not found"}), 404


# Enter the Flask application context.
# This allows SQLAlchemy to work with the Flask app.
with app.app_context():

    # Create the database tables if they don't already exist.
    db.create_all()


# Only run the server if this Python file is executed directly.
if __name__ == "__main__":

    # Start the Flask development server.
    # 127.0.0.1 means the server runs on your computer.
    # port 3000 means the API is available on port 3000.
    app.run(host="127.0.0.1", port=3000)