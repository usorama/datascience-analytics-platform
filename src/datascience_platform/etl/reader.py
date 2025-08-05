"""Data reading functionality for the DataScience Analytics Platform."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import polars as pl
from pydantic import BaseModel, Field, field_validator

from datascience_platform.core.config import settings
from datascience_platform.core.exceptions import DataReaderError, ETLError


class ReadOptions(BaseModel):
    """Configuration options for data reading."""
    
    chunk_size: Optional[int] = Field(default=None, description="Number of rows to read per chunk")
    skip_rows: int = Field(default=0, ge=0, description="Number of rows to skip at the beginning")
    max_rows: Optional[int] = Field(default=None, ge=1, description="Maximum number of rows to read")
    encoding: str = Field(default="utf-8", description="File encoding")
    delimiter: Optional[str] = Field(default=None, description="Column delimiter for CSV files")
    header: Union[bool, int, List[int]] = Field(default=True, description="Row(s) to use as column names")
    na_values: Optional[List[str]] = Field(default=None, description="Additional strings to recognize as NA/NaN")
    dtype: Optional[Dict[str, str]] = Field(default=None, description="Data types for columns")
    parse_dates: Optional[List[str]] = Field(default=None, description="Columns to parse as dates")
    use_polars: bool = Field(default=True, description="Use Polars for data processing")
    
    @field_validator("chunk_size")
    @classmethod
    def validate_chunk_size(cls, v: Optional[int]) -> Optional[int]:
        """Validate chunk size."""
        if v is not None and v <= 0:
            raise ValueError("chunk_size must be positive")
        return v


class DataReader:
    """Universal data reader supporting multiple file formats."""
    
    def __init__(self, options: Optional[ReadOptions] = None) -> None:
        """Initialize data reader.
        
        Args:
            options: Reading options and configuration
        """
        self.options = options or ReadOptions()
        self._supported_formats = set(settings.supported_formats)
    
    def read(
        self,
        file_path: Union[str, Path],
        format: Optional[str] = None,
        **kwargs: Any
    ) -> Union[pd.DataFrame, pl.DataFrame]:
        """Read data from file.
        
        Args:
            file_path: Path to the data file
            format: File format (auto-detected if not provided)
            **kwargs: Additional arguments to override default options
            
        Returns:
            DataFrame with loaded data
            
        Raises:
            DataReaderError: If file cannot be read or format is unsupported
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise DataReaderError(f"File not found: {file_path}", file_path=str(file_path))
        
        # Auto-detect format if not provided
        if format is None:
            format = self._detect_format(file_path)
        
        format = format.lower()
        if format not in self._supported_formats:
            raise DataReaderError(
                f"Unsupported file format: {format}. Supported formats: {self._supported_formats}",
                file_path=str(file_path),
                file_format=format
            )
        
        # Merge kwargs with default options
        read_options = self.options.dict()
        read_options.update(kwargs)
        
        try:
            if format == "csv":
                return self._read_csv(file_path, **read_options)
            elif format == "json":
                return self._read_json(file_path, **read_options)
            elif format == "parquet":
                return self._read_parquet(file_path, **read_options)
            elif format in ["xlsx", "xls"]:
                return self._read_excel(file_path, **read_options)
            else:
                raise DataReaderError(
                    f"No reader implementation for format: {format}",
                    file_path=str(file_path),
                    file_format=format
                )
        except Exception as e:
            if isinstance(e, DataReaderError):
                raise
            raise DataReaderError(
                f"Error reading {format} file: {str(e)}",
                file_path=str(file_path),
                file_format=format
            ) from e
    
    def read_chunked(
        self,
        file_path: Union[str, Path],
        chunk_size: Optional[int] = None,
        **kwargs: Any
    ) -> Union[pd.core.groupby.DataFrameGroupBy, List[Union[pd.DataFrame, pl.DataFrame]]]:
        """Read data in chunks for large files.
        
        Args:
            file_path: Path to the data file
            chunk_size: Size of each chunk (uses default if not provided)
            **kwargs: Additional reading arguments
            
        Returns:
            Iterator or list of DataFrame chunks
        """
        chunk_size = chunk_size or self.options.chunk_size or settings.default_chunk_size
        
        # Update options for chunked reading
        kwargs.update({"chunk_size": chunk_size})
        
        file_path = Path(file_path)
        format = self._detect_format(file_path)
        
        if format == "csv":
            return self._read_csv_chunked(file_path, chunk_size, **kwargs)
        else:
            # For non-CSV formats, read full file and split into chunks
            df = self.read(file_path, **kwargs)
            return self._split_dataframe_chunks(df, chunk_size)
    
    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Get information about a data file.
        
        Args:
            file_path: Path to the data file
            
        Returns:
            Dictionary with file information
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise DataReaderError(f"File not found: {file_path}", file_path=str(file_path))
        
        format = self._detect_format(file_path)
        file_size = file_path.stat().st_size
        
        info = {
            "file_path": str(file_path),
            "format": format,
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2),
            "exists": True,
        }
        
        # Try to get additional metadata
        try:
            if format == "csv":
                # Quick scan of CSV file
                with open(file_path, 'r', encoding=self.options.encoding) as f:
                    first_line = f.readline().strip()
                    if first_line:
                        info["estimated_columns"] = len(first_line.split(self.options.delimiter or ","))
                
                # Estimate row count
                with open(file_path, 'r', encoding=self.options.encoding) as f:
                    row_count = sum(1 for _ in f)
                    if self.options.header:
                        row_count -= 1
                info["estimated_rows"] = row_count
                
        except Exception:
            # If metadata extraction fails, continue without it
            pass
        
        return info
    
    def _detect_format(self, file_path: Path) -> str:
        """Detect file format from extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected file format
        """
        suffix = file_path.suffix.lower()
        format_mapping = {
            ".csv": "csv",
            ".json": "json",
            ".jsonl": "json",
            ".parquet": "parquet",
            ".xlsx": "xlsx",
            ".xls": "xls",
        }
        
        format = format_mapping.get(suffix)
        if format is None:
            raise DataReaderError(f"Cannot detect format for file: {file_path}")
        
        return format
    
    def _read_csv(self, file_path: Path, **kwargs: Any) -> Union[pd.DataFrame, pl.DataFrame]:
        """Read CSV file."""
        use_polars = kwargs.pop("use_polars", self.options.use_polars)
        
        read_args = {
            "encoding": kwargs.get("encoding", self.options.encoding),
            "skip_rows": kwargs.get("skip_rows", self.options.skip_rows),
        }
        
        if kwargs.get("max_rows"):
            read_args["n_rows"] = kwargs["max_rows"]
        
        if kwargs.get("delimiter"):
            read_args["separator"] = kwargs["delimiter"]
        
        if kwargs.get("header") is not None:
            if isinstance(kwargs["header"], bool):
                read_args["has_header"] = kwargs["header"]
            else:
                read_args["skip_rows_after_header"] = kwargs["header"]
        
        if use_polars:
            return pl.read_csv(str(file_path), **read_args)
        else:
            # Convert to pandas arguments
            pandas_args = {
                "encoding": read_args.get("encoding"),
                "skiprows": read_args.get("skip_rows", 0),
                "nrows": read_args.get("n_rows"),
                "sep": read_args.get("separator", ","),
                "header": 0 if read_args.get("has_header", True) else None,
            }
            
            # Remove None values
            pandas_args = {k: v for k, v in pandas_args.items() if v is not None}
            
            return pd.read_csv(str(file_path), **pandas_args)
    
    def _read_json(self, file_path: Path, **kwargs: Any) -> Union[pd.DataFrame, pl.DataFrame]:
        """Read JSON file."""
        use_polars = kwargs.pop("use_polars", self.options.use_polars)
        
        try:
            with open(file_path, 'r', encoding=kwargs.get("encoding", self.options.encoding)) as f:
                data = json.load(f)
            
            if use_polars:
                return pl.DataFrame(data)
            else:
                return pd.DataFrame(data)
                
        except json.JSONDecodeError as e:
            raise DataReaderError(f"Invalid JSON format: {str(e)}", file_path=str(file_path), file_format="json")
    
    def _read_parquet(self, file_path: Path, **kwargs: Any) -> Union[pd.DataFrame, pl.DataFrame]:
        """Read Parquet file."""
        use_polars = kwargs.pop("use_polars", self.options.use_polars)
        
        if use_polars:
            return pl.read_parquet(str(file_path))
        else:
            return pd.read_parquet(str(file_path))
    
    def _read_excel(self, file_path: Path, **kwargs: Any) -> Union[pd.DataFrame, pl.DataFrame]:
        """Read Excel file."""
        use_polars = kwargs.pop("use_polars", self.options.use_polars)
        
        read_args = {
            "skiprows": kwargs.get("skip_rows", self.options.skip_rows),
            "nrows": kwargs.get("max_rows"),
            "header": 0 if kwargs.get("header", self.options.header) else None,
        }
        
        # Remove None values
        read_args = {k: v for k, v in read_args.items() if v is not None}
        
        df = pd.read_excel(str(file_path), **read_args)
        
        if use_polars:
            return pl.from_pandas(df)
        else:
            return df
    
    def _read_csv_chunked(
        self,
        file_path: Path,
        chunk_size: int,
        **kwargs: Any
    ) -> Union[pd.core.groupby.DataFrameGroupBy, List[Union[pd.DataFrame, pl.DataFrame]]]:
        """Read CSV file in chunks."""
        use_polars = kwargs.pop("use_polars", self.options.use_polars)
        
        if use_polars:
            # Polars doesn't have built-in chunked reading, so read full file and split
            df = self._read_csv(file_path, use_polars=True, **kwargs)
            return self._split_dataframe_chunks(df, chunk_size)
        else:
            # Use pandas chunked reading
            read_args = {
                "encoding": kwargs.get("encoding", self.options.encoding),
                "skiprows": kwargs.get("skip_rows", self.options.skip_rows),
                "sep": kwargs.get("delimiter", ","),
                "header": 0 if kwargs.get("header", self.options.header) else None,
                "chunksize": chunk_size,
            }
            
            # Remove None values
            read_args = {k: v for k, v in read_args.items() if v is not None}
            
            return pd.read_csv(str(file_path), **read_args)
    
    def _split_dataframe_chunks(
        self,
        df: Union[pd.DataFrame, pl.DataFrame],
        chunk_size: int
    ) -> List[Union[pd.DataFrame, pl.DataFrame]]:
        """Split DataFrame into chunks."""
        chunks = []
        total_rows = len(df)
        
        for i in range(0, total_rows, chunk_size):
            chunk = df[i:i + chunk_size]
            chunks.append(chunk)
        
        return chunks