# remarcableclient

A Python connector for the Remarcable API, providing access to asset status, projects, users, tool requests, and more.

## Installation

```sh
pip install remarcableclient
```

## Build

```sh
uv build
```

The output `.whl` will be generated in `dist/`

## Requirements
- Python >= 3.10
- pandas >= 2.3.0
- requests >= 2.32.4

## Usage

```py
from remarcable_client import RemarcableClient, RemarcableConfig

config = RemarcableConfig(
    api_key="YOUR_API_KEY",  # or email="...", password="..."
)
client = RemarcableClient(config)

# Example: List all projects
projects = client.projects.list_projects()
print(projects)
```

## Resources
The client exposes the following resource modules:

- `client.assets` — Asset management (items, requests, transfers, charges, etc.)
- `client.orders` — Purchase and sales order management
- `client.invoices` — Invoice and invoice item management
- `client.price_files` — Price file and item management
- `client.projects` — Project and project category management
- `client.users` — User account management
- `client.vendors` — Vendor and supplier management

Each resource provides methods for listing, retrieving, creating, and updating records. See the docstrings in the source code for detailed parameter and return value documentation.