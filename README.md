# shqaff

## Overview

shqaff is a minimal task queue built with Python and SQLAlchemy. It stores jobs in a PostgreSQL table and processes them with registered consumers.

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure database settings with environment variables such as `SHAQAFF_DB_HOST` and `SHAQAFF_DB_NAME` or rely on defaults.

## Usage

1. Initialize the database and start the example process:
   ```bash
   python main.py
   ```
2. The demo task creates a payload and processes it through a consumer.

## Testing

Run the test suite:
```bash
pytest
```
