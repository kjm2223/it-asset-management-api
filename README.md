# IT Asset Management API

A RESTful API built with Python and Flask for managing IT assets such as laptops, desktops, and other equipment.

## Features

- Create IT assets
- View all assets
- View individual assets by ID
- Update existing assets
- Delete assets
- SQLite database persistence
- Input validation and error handling
- API key authentication
- Environment variable protection using `.env`

## Technologies

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- REST API
- Git / GitHub

## API Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/assets` | Retrieve all IT assets | No |
| GET | `/assets/<id>` | Retrieve a specific asset | No |
| POST | `/assets` | Create a new asset | API Key |
| PUT | `/assets/<id>` | Update an existing asset | API Key |
| DELETE | `/assets/<id>` | Delete an asset | API Key |

## Example Asset

```json
{
  "id": 1,
  "asset_name": "MacBook Pro",
  "asset_type": "Laptop",
  "status": "Active"
}

## Installation and Setup

1. Clone the repository:

```bash
git clone https://github.com/kjm2223/it-asset-management-api.git
```

2. Navigate into the project:

```bash
cd it-asset-management-api
```

3. Install the required dependencies:

```bash
pip3 install -r requirements.txt
```

4. Create a `.env` file in the project directory:

```text
API_KEY=your_api_key_here
```

5. Start the Flask API:

```bash
python3 Api.py
```

The API will run locally at `http://127.0.0.1:3000`.