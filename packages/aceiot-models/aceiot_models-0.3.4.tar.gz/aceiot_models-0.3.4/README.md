# aceiot-models

Pydantic models and API client for the ACE IoT Aerodrome Platform

## Installation

```bash
pip install aceiot-models
```

For upload progress support:
```bash
pip install aceiot-models[upload-progress]
```

## Features

- **Pydantic Models**: Type-safe data models for all ACE IoT entities
- **API Client**: Comprehensive Python SDK for the ACE IoT API
- **Pagination Support**: Efficient handling of large datasets
- **Batch Processing**: Process large operations in manageable chunks
- **Type Hints**: Full type annotations for better IDE support
- **Error Handling**: Robust error handling with detailed error information

## Usage

### Using the API Client

```python
from aceiot_models.api import APIClient, APIError

# Initialize the client
client = APIClient(
    base_url="https://flightdeck.aceiot.cloud/api",
    api_key="your-api-key"
)

# Or use environment variables:
# export ACEIOT_API_URL=https://flightdeck.aceiot.cloud/api
# export ACEIOT_API_KEY=your-api-key
client = APIClient()

# Get clients
clients = client.get_clients(page=1, per_page=20)

# Create a point
from aceiot_models import PointCreate

point = PointCreate(
    name="sensor/temperature/office",
    site_id=1,
    client_id=1,
    point_type="analog",
    collect_enabled=True
)
result = client.create_points([point.model_dump()])
```

### Using Pagination

```python
from aceiot_models.api import PaginatedResults

# Paginate through all sites
paginator = PaginatedResults(client.get_sites, per_page=100)
for page_sites in paginator:
    for site in page_sites:
        print(f"Site: {site['name']}")

# Or get all items at once
all_sites = paginator.all_items()
```

### Batch Processing

```python
from aceiot_models.api import batch_process

# Process points in batches
points = [...]  # List of many points

def create_batch(batch):
    return client.create_points(batch)

results = batch_process(
    items=points,
    process_func=create_batch,
    batch_size=100,
    progress_callback=lambda current, total: print(f"{current}/{total}")
)
```

### Using the Models

```python
from aceiot_models import Point, Sample, PointCreate

# Create a new point
point = PointCreate(
    name="sensor/temperature/office",
    site_id=1,
    client_id=1,
    point_type="analog",
    collect_enabled=True
)
```

### Using the API Client

```python
from aceiot_models.api import APIClient, APIError

# Initialize the client
client = APIClient(
    base_url="https://flightdeck.aceiot.cloud/api",
    api_key="your-api-key"
)

# Fetch sites
try:
    sites = client.get_sites(page=1, per_page=100)
    print(f"Found {sites['total_items']} sites")
except APIError as e:
    print(f"Error: {e}")
```

### Pagination

```python
from aceiot_models.api import PaginatedResults

# Iterate through all points page by page
paginator = PaginatedResults(client.get_points, per_page=500)
for page_points in paginator:
    print(f"Processing {len(page_points)} points...")
    # Process each page

# Or get all items at once
all_points = paginator.all_items()
```

### Batch Processing

```python
from aceiot_models.api import batch_process

# Process items in batches
def process_batch(items):
    return client.create_points(items)

results = batch_process(
    items=large_list_of_points,
    process_func=process_batch,
    batch_size=100,
    progress_callback=lambda current, total: print(f"{current}/{total}")
)
```

## Configuration

The API client can be configured through environment variables:

- `ACEIOT_API_URL`: Base URL for the API
- `ACEIOT_API_KEY`: Your API key
- `ACEIOT_API_TIMEOUT`: Request timeout in seconds (default: 30)

## Examples

See the [examples directory](examples/) for complete usage examples.

## Testing

### Unit Tests

Run the unit tests:

```bash
pytest tests/ -v
```

### Integration Tests

Integration tests verify the API client works with a real API endpoint. See [tests/api/README_INTEGRATION.md](tests/api/README_INTEGRATION.md) for setup instructions.

```bash
# Set environment variables
export ACEIOT_API_URL="https://flightdeck.aceiot.cloud/api"
export ACEIOT_API_KEY="your-api-key"
export ACEIOT_INTEGRATION_TESTS="true"

# Run integration tests
pytest tests/api/test_integration.py -v
```

## Development

This project uses `uv` for dependency management. To set up a development environment:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/yourusername/aceiot-models.git
cd aceiot-models

# Install dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Run linting
uv run ruff check .
uv run ruff format .

# Run type checking
uv run pyrefly check aceiot_models/
```

## License

MIT License
