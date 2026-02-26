# shqaff

[![PyPI version](https://img.shields.io/pypi/v/shqaff)](https://pypi.org/project/shqaff/)
[![Python](https://img.shields.io/pypi/pyversions/shqaff)](https://pypi.org/project/shqaff/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📋 Overview

shqaff is a minimal task queue built with Python and SQLAlchemy. It stores jobs in a PostgreSQL table and processes them with registered consumers.

## 📦 Installation

1. Install dependencies:
   ```bash
   pip install shqaff
   ```
2. Configure database settings with environment variables such as `SHAQAFF_DB_HOST` and `SHAQAFF_DB_NAME` or rely on defaults.

## 🚀 Usage

1. Initialize the database and start the example process:
   ```bash
   python main.py
   ```
2. The demo task creates a payload and processes it through a consumer.

## 🧪 Testing

Run the test suite:
```bash
pytest
```
