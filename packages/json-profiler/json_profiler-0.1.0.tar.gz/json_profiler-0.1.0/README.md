# JSON Profiler

A Python tool for exploring and analyzing JSON structure with aggregated statistics. This package helps you understand the structure of complex JSON data by providing detailed insights into field types, presence percentages, and nested structures.

## Installation

```bash
pip install json-profiler
```

## Usage

```python
from json_profiler import explore_json_aggregated
import json

# Example JSON data
data = {
    "users": [
        {"id": 1, "name": "Alice", "email": "alice@example.com", "tags": ["admin", "user"]},
        {"id": 2, "name": "Bob", "email": "bob@example.com", "tags": []},
        {"id": 3, "name": "Charlie", "tags": ["user"]}
    ],
    "metadata": {
        "total": 3,
        "active": True
    }
}

# Analyze the JSON structure
result = explore_json_aggregated(data)
```

This will output:
```
=== AGGREGATED STRUCTURE ===
users[] (total items: 3 across 1 list instances):
  email: str (66.7% present)
  id: int (100.0% present)  
  name: str (100.0% present)
  tags: list (100.0% present) [WARNING: 1/3 lists empty (33.3%)]

ROOT[] (total items: 1 across 1 list instances):
  active: bool (100.0% present)
  total: int (100.0% present)
```

## Features

- **Field Analysis**: Shows data types and presence percentages for each field
- **Nested Structure Support**: Handles deeply nested JSON objects and arrays
- **Empty List Detection**: Warns about empty lists in your data
- **Aggregated Statistics**: Provides comprehensive statistics across all instances
- **Type Information**: Shows all data types encountered for each field

## Return Value

The function returns a dictionary containing all unique values found for each field across the entire JSON structure.

## License

MIT License