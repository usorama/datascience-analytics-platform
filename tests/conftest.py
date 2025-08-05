"""Pytest configuration and fixtures for the DataScience Analytics Platform tests."""

import tempfile
import json
import gzip
from pathlib import Path
from typing import Any, Dict, Generator
from datetime import datetime, timedelta
import random

import pandas as pd
import polars as pl
import pytest
import numpy as np

from datascience_platform.core.config import Settings
from datascience_platform.etl.schema import ColumnSchema, DataSchema


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_csv_file(temp_dir: Path) -> Path:
    """Create a sample CSV file for testing."""
    csv_data = """id,name,age,email,status,score
1,Alice,25,alice@example.com,active,85.5
2,Bob,30,bob@example.com,inactive,92.3
3,Charlie,22,charlie@example.com,pending,78.1
4,Diana,28,diana@example.com,active,96.7
5,Eve,35,eve@example.com,active,88.9
"""
    csv_file = temp_dir / "sample.csv"
    csv_file.write_text(csv_data)
    return csv_file


@pytest.fixture
def sample_json_file(temp_dir: Path) -> Path:
    """Create a sample JSON file for testing."""
    json_data = [
        {"id": 1, "name": "Alice", "age": 25, "email": "alice@example.com", "status": "active", "score": 85.5},
        {"id": 2, "name": "Bob", "age": 30, "email": "bob@example.com", "status": "inactive", "score": 92.3},
        {"id": 3, "name": "Charlie", "age": 22, "email": "charlie@example.com", "status": "pending", "score": 78.1},
        {"id": 4, "name": "Diana", "age": 28, "email": "diana@example.com", "status": "active", "score": 96.7},
        {"id": 5, "name": "Eve", "age": 35, "email": "eve@example.com", "status": "active", "score": 88.9},
    ]
    
    import json
    json_file = temp_dir / "sample.json"
    json_file.write_text(json.dumps(json_data, indent=2))
    return json_file


@pytest.fixture
def sample_pandas_dataframe() -> pd.DataFrame:
    """Create a sample pandas DataFrame for testing."""
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
        "age": [25, 30, 22, 28, 35],
        "email": ["alice@example.com", "bob@example.com", "charlie@example.com", 
                 "diana@example.com", "eve@example.com"],
        "status": ["active", "inactive", "pending", "active", "active"],
        "score": [85.5, 92.3, 78.1, 96.7, 88.9]
    })


@pytest.fixture
def sample_polars_dataframe() -> pl.DataFrame:
    """Create a sample polars DataFrame for testing."""
    return pl.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
        "age": [25, 30, 22, 28, 35],
        "email": ["alice@example.com", "bob@example.com", "charlie@example.com", 
                 "diana@example.com", "eve@example.com"],
        "status": ["active", "inactive", "pending", "active", "active"],
        "score": [85.5, 92.3, 78.1, 96.7, 88.9]
    })


@pytest.fixture
def sample_schema() -> DataSchema:
    """Create a sample data schema for testing."""
    columns = [
        ColumnSchema(
            name="id",
            dtype="int64",
            nullable=False,
            unique=True,
            min_value=1,
            description="Unique identifier"
        ),
        ColumnSchema(
            name="name",
            dtype="string",
            nullable=False,
            description="Name field"
        ),
        ColumnSchema(
            name="age",
            dtype="int32",
            nullable=True,
            min_value=0,
            max_value=150,
            description="Age in years"
        ),
        ColumnSchema(
            name="email",
            dtype="string",
            nullable=True,
            regex_pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            description="Email address"
        ),
        ColumnSchema(
            name="status",
            dtype="string",
            nullable=False,
            allowed_values=["active", "inactive", "pending"],
            description="Account status"
        ),
        ColumnSchema(
            name="score",
            dtype="float64",
            nullable=True,
            min_value=0.0,
            max_value=100.0,
            description="Performance score"
        )
    ]
    
    return DataSchema(
        name="test_schema",
        version="1.0.0",
        description="Test schema for unit tests",
        columns=columns,
        primary_key=["id"]
    )


@pytest.fixture
def invalid_dataframe() -> pd.DataFrame:
    """Create an invalid DataFrame for testing validation failures."""
    return pd.DataFrame({
        "id": [1, 2, 2, None, 5],  # Duplicate and null in primary key
        "name": ["Alice", "Bob", "", None, "Eve"],  # Empty and null names
        "age": [25, 200, -5, 28, 35],  # Out of range ages
        "email": ["alice@example.com", "invalid-email", "charlie@example.com", 
                 "diana@example.com", "eve@example.com"],  # Invalid email format
        "status": ["active", "unknown", "pending", "active", "active"],  # Invalid status
        "score": [85.5, 150.0, -10.0, 96.7, 88.9]  # Out of range scores
    })


@pytest.fixture
def test_settings() -> Settings:
    """Create test-specific settings."""
    return Settings(
        debug=True,
        default_chunk_size=3,
        max_memory_usage_gb=1.0,
        validation_strict=True,
        log_level="DEBUG"
    )


@pytest.fixture
def mock_config(test_settings: Settings, monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock the global settings for tests."""
    monkeypatch.setattr("datascience_platform.core.config.settings", test_settings)


@pytest.fixture
def large_csv_file(temp_dir: Path) -> Path:
    """Create a large CSV file for testing chunked reading."""
    csv_file = temp_dir / "large_sample.csv"
    
    # Create a larger dataset
    data = []
    for i in range(100):
        data.append(f"{i+1},User{i+1},{20 + (i % 50)},user{i+1}@example.com,{'active' if i % 2 == 0 else 'inactive'},{50 + (i % 50)}.{i % 10}")
    
    csv_content = "id,name,age,email,status,score\n" + "\n".join(data)
    csv_file.write_text(csv_content)
    return csv_file


@pytest.fixture
def parquet_file(temp_dir: Path, sample_pandas_dataframe: pd.DataFrame) -> Path:
    """Create a sample Parquet file for testing."""
    parquet_file = temp_dir / "sample.parquet"
    sample_pandas_dataframe.to_parquet(parquet_file, index=False)
    return parquet_file


@pytest.fixture(scope="session")
def sample_data_dict() -> Dict[str, Any]:
    """Shared sample data dictionary for tests."""
    return {
        "users": [
            {"id": 1, "name": "Alice", "active": True},
            {"id": 2, "name": "Bob", "active": False},
            {"id": 3, "name": "Charlie", "active": True},
        ],
        "metadata": {
            "created": "2024-01-01",
            "version": "1.0.0",
            "total_records": 3
        }
    }


@pytest.fixture
def time_series_csv_file(temp_dir: Path) -> Path:
    """Create a time series CSV file for testing."""
    base_date = datetime(2024, 1, 1)
    csv_data = ["timestamp,value,category,location"]
    
    for i in range(100):
        timestamp = base_date + timedelta(days=i)
        value = 100 + 10 * np.sin(i * 0.1) + random.gauss(0, 2)
        category = random.choice(['A', 'B', 'C'])
        location = random.choice(['North', 'South', 'East', 'West'])
        
        csv_data.append(f"{timestamp.isoformat()},{value:.2f},{category},{location}")
    
    csv_file = temp_dir / "timeseries.csv"
    csv_file.write_text("\n".join(csv_data))
    return csv_file


@pytest.fixture
def financial_data_csv(temp_dir: Path) -> Path:
    """Create a financial dataset CSV for testing."""
    csv_data = ["date,symbol,open,high,low,close,volume,market_cap"]
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
    base_date = datetime(2024, 1, 1)
    
    for i in range(50):
        date = base_date + timedelta(days=i)
        for symbol in symbols:
            open_price = 100 + random.gauss(0, 20)
            high = open_price + random.uniform(0, 10)
            low = open_price - random.uniform(0, 10)
            close = open_price + random.gauss(0, 5)
            volume = random.randint(1000000, 50000000)
            market_cap = close * 1000000000
            
            csv_data.append(f"{date.date()},{symbol},{open_price:.2f},{high:.2f},{low:.2f},{close:.2f},{volume},{market_cap:.0f}")
    
    csv_file = temp_dir / "financial_data.csv"
    csv_file.write_text("\n".join(csv_data))
    return csv_file


@pytest.fixture
def multilang_csv_file(temp_dir: Path) -> Path:
    """Create a CSV file with international characters for encoding tests."""
    csv_data = "id,name,city,description\n"
    csv_data += "1,José García,São Paulo,Descripción en español\n"
    csv_data += "2,李明,北京,中文描述信息\n"
    csv_data += "3,Владимир,Москва,Описание на русском\n"
    csv_data += "4,François,Paris,Description en français\n"
    csv_data += "5,Müller,Berlin,Beschreibung auf Deutsch\n"
    
    csv_file = temp_dir / "multilang.csv"
    csv_file.write_text(csv_data, encoding='utf-8')
    return csv_file


@pytest.fixture
def nested_json_file(temp_dir: Path) -> Path:
    """Create a nested JSON file for complex data testing."""
    nested_data = [
        {
            "id": 1,
            "user": {
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "preferences": {
                    "theme": "dark",
                    "notifications": True,
                    "language": "en"
                }
            },
            "metrics": {
                "login_count": 45,
                "last_login": "2024-01-15T10:30:00Z",
                "performance_scores": [85.5, 92.3, 78.1, 96.7]
            },
            "tags": ["premium", "active", "verified"]
        },
        {
            "id": 2,
            "user": {
                "name": "Bob Smith",
                "email": "bob@example.com",
                "preferences": {
                    "theme": "light",
                    "notifications": False,
                    "language": "es"
                }
            },
            "metrics": {
                "login_count": 23,
                "last_login": "2024-01-10T14:22:00Z",
                "performance_scores": [67.2, 84.5, 91.3]
            },
            "tags": ["standard", "inactive"]
        }
    ]
    
    json_file = temp_dir / "nested.json"
    json_file.write_text(json.dumps(nested_data, indent=2))
    return json_file


@pytest.fixture
def compressed_csv_file(temp_dir: Path) -> Path:
    """Create a gzip-compressed CSV file for compression testing."""
    csv_data = "id,data,value\n"
    for i in range(1000):
        csv_data += f"{i},data_{i},{i * 2.5}\n"
    
    csv_file = temp_dir / "compressed.csv.gz"
    with gzip.open(csv_file, 'wt', encoding='utf-8') as f:
        f.write(csv_data)
    
    return csv_file


@pytest.fixture
def excel_file(temp_dir: Path) -> Path:
    """Create an Excel file for testing (if openpyxl is available)."""
    try:
        df = pd.DataFrame({
            'id': range(1, 11),
            'name': [f'Item_{i}' for i in range(1, 11)],
            'value': [i * 10.5 for i in range(1, 11)],
            'category': ['A' if i % 2 == 0 else 'B' for i in range(1, 11)],
            'date': pd.date_range('2024-01-01', periods=10)
        })
        
        excel_file = temp_dir / "sample.xlsx"
        df.to_excel(excel_file, index=False)
        return excel_file
    except ImportError:
        pytest.skip("openpyxl not available for Excel file testing")


@pytest.fixture
def malformed_csv_file(temp_dir: Path) -> Path:
    """Create a malformed CSV file for error handling tests."""
    malformed_data = """id,name,value
1,Alice,100
2,"Bob,Smith",200
3,Charlie,
4,Diana,400,extra_column
5,Eve"""  # Missing value at end
    
    csv_file = temp_dir / "malformed.csv"
    csv_file.write_text(malformed_data)
    return csv_file


@pytest.fixture
def empty_csv_file(temp_dir: Path) -> Path:
    """Create an empty CSV file for edge case testing."""
    csv_file = temp_dir / "empty.csv"
    csv_file.write_text("")
    return csv_file


@pytest.fixture
def headers_only_csv_file(temp_dir: Path) -> Path:
    """Create a CSV file with only headers for edge case testing."""
    csv_file = temp_dir / "headers_only.csv"
    csv_file.write_text("id,name,email,status,score\n")
    return csv_file


@pytest.fixture
def very_wide_csv_file(temp_dir: Path) -> Path:
    """Create a CSV file with many columns for performance testing."""
    columns = ['id'] + [f'col_{i}' for i in range(100)]
    header = ','.join(columns)
    
    data_rows = [header]
    for i in range(50):
        row = [str(i)] + [str(random.random()) for _ in range(100)]
        data_rows.append(','.join(row))
    
    csv_file = temp_dir / "wide.csv"
    csv_file.write_text('\n'.join(data_rows))
    return csv_file


@pytest.fixture
def database_schema() -> DataSchema:
    """Create a comprehensive database-like schema for testing."""
    columns = [
        ColumnSchema(
            name="user_id",
            dtype="int64",
            nullable=False,
            unique=True,
            min_value=1,
            description="Primary key - unique user identifier"
        ),
        ColumnSchema(
            name="username",
            dtype="string",
            nullable=False,
            unique=True,
            min_length=3,
            max_length=50,
            regex_pattern=r"^[a-zA-Z0-9_]+$",
            description="Unique username"
        ),
        ColumnSchema(
            name="email",
            dtype="string",
            nullable=False,
            unique=True,
            regex_pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            description="User email address"
        ),
        ColumnSchema(
            name="created_at",
            dtype="datetime64[ns]",
            nullable=False,
            description="Account creation timestamp"
        ),
        ColumnSchema(
            name="age",
            dtype="int32",
            nullable=True,
            min_value=13,
            max_value=120,
            description="User age in years"
        ),
        ColumnSchema(
            name="balance",
            dtype="float64",
            nullable=False,
            min_value=0.0,
            description="Account balance in USD"
        ),
        ColumnSchema(
            name="account_type",
            dtype="string",
            nullable=False,
            allowed_values=["free", "premium", "enterprise"],
            description="Account subscription type"
        ),
        ColumnSchema(
            name="is_verified",
            dtype="bool",
            nullable=False,
            description="Whether account is verified"
        ),
        ColumnSchema(
            name="last_login",
            dtype="datetime64[ns]",
            nullable=True,
            description="Last login timestamp"
        ),
        ColumnSchema(
            name="profile_completion",
            dtype="float64",
            nullable=True,
            min_value=0.0,
            max_value=100.0,
            description="Profile completion percentage"
        )
    ]
    
    return DataSchema(
        name="user_database_schema",
        version="2.0.0",
        description="Comprehensive schema for user database",
        columns=columns,
        primary_key=["user_id"],
        indexes=["email", "username", "created_at"]
    )


@pytest.fixture
def ml_dataset_file(temp_dir: Path) -> Path:
    """Create a dataset suitable for ML testing."""
    np.random.seed(42)  # For reproducible results
    
    n_samples = 500
    data = {
        'feature_1': np.random.normal(0, 1, n_samples),
        'feature_2': np.random.normal(2, 1.5, n_samples),
        'feature_3': np.random.uniform(-1, 1, n_samples),
        'categorical_1': np.random.choice(['A', 'B', 'C'], n_samples),
        'categorical_2': np.random.choice(['X', 'Y'], n_samples, p=[0.7, 0.3]),
        'date_feature': pd.date_range('2023-01-01', periods=n_samples, freq='D'),
        'binary_feature': np.random.choice([0, 1], n_samples, p=[0.4, 0.6])
    }
    
    # Create target variable with some relationship to features
    data['target'] = (
        0.5 * data['feature_1'] + 
        0.3 * data['feature_2'] + 
        0.2 * data['feature_3'] + 
        np.where(data['categorical_1'] == 'A', 1, 0) +
        np.random.normal(0, 0.1, n_samples)
    )
    
    df = pd.DataFrame(data)
    ml_file = temp_dir / "ml_dataset.csv"
    df.to_csv(ml_file, index=False)
    return ml_file


@pytest.fixture
def performance_test_config() -> Dict[str, Any]:
    """Configuration for performance testing."""
    return {
        'small_dataset_size': 1000,
        'medium_dataset_size': 10000,
        'large_dataset_size': 100000,
        'timeout_seconds': 30,
        'memory_limit_mb': 500,
        'acceptable_slowdown_factor': 10
    }


@pytest.fixture
def mock_external_api():
    """Mock external API responses for testing."""
    class MockAPI:
        def __init__(self):
            self.call_count = 0
            
        def get_data(self, endpoint: str):
            self.call_count += 1
            if endpoint == "users":
                return {"users": [{"id": 1, "name": "Test User"}]}
            elif endpoint == "error":
                raise Exception("API Error")
            return {"data": f"mock_data_for_{endpoint}"}
    
    return MockAPI()


# Custom markers for organizing tests
def pytest_configure(config: pytest.Config) -> None:
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "performance: Performance benchmark tests")
    config.addinivalue_line("markers", "cli: CLI command tests")
    config.addinivalue_line("markers", "etl: ETL operation tests")
    config.addinivalue_line("markers", "validation: Data validation tests")
    config.addinivalue_line("markers", "ml: Machine Learning tests")
    config.addinivalue_line("markers", "dashboard: Dashboard generation tests")
    config.addinivalue_line("markers", "regression: Regression tests")
    config.addinivalue_line("markers", "security: Security-related tests")


# Test data cleanup
@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Automatically cleanup test data after each test."""
    yield
    # Cleanup code can go here if needed
    pass