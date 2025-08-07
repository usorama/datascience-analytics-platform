"""Robust Data Validation and Preprocessing for ADO Analytics

This module provides comprehensive data validation and preprocessing
to handle various data quality issues and edge cases.
"""

import pandas as pd
import numpy as np
import polars as pl
from typing import Dict, List, Any, Optional, Union, Tuple
import re
from datetime import datetime
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DataValidationError(Exception):
    """Custom exception for data validation errors."""
    pass


class DataTypeInferencer:
    """Intelligently infer and fix data types."""
    
    def __init__(self):
        # Patterns for different data types
        self.patterns = {
            'integer': re.compile(r'^-?\d+$'),
            'decimal': re.compile(r'^-?\d*\.?\d+([eE][+-]?\d+)?$'),
            'percentage': re.compile(r'^-?\d*\.?\d+\s*%$'),
            'currency': re.compile(r'^[$£€¥]\s*-?\d*\.?\d+$|^-?\d*\.?\d+\s*[$£€¥]$'),
            'date': re.compile(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}'),
            'boolean': re.compile(r'^(true|false|yes|no|y|n|1|0)$', re.IGNORECASE),
            'work_item_id': re.compile(r'^[A-Z]+-\d+$|^\d+$'),
            'story_points': re.compile(r'^\d+(\.\d)?$'),  # Allow 0.5, 1, 2, 3, etc.
        }
        
        # Common date formats to try
        self.date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d',
            '%m-%d-%Y', '%d-%m-%Y', '%Y-%m-%d %H:%M:%S',
            '%m/%d/%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S'
        ]
    
    def infer_column_type(self, series: pd.Series) -> str:
        """Infer the data type of a pandas series."""
        # Remove nulls for analysis
        non_null = series.dropna()
        
        if len(non_null) == 0:
            return 'unknown'
        
        # Sample values for efficiency
        sample_size = min(100, len(non_null))
        sample = non_null.sample(n=sample_size, random_state=42) if len(non_null) > sample_size else non_null
        
        # Check each pattern
        type_counts = {
            'integer': 0,
            'decimal': 0,
            'percentage': 0,
            'currency': 0,
            'date': 0,
            'boolean': 0,
            'text': 0
        }
        
        for value in sample:
            str_val = str(value).strip()
            
            # Check patterns in order of specificity
            if self.patterns['percentage'].match(str_val):
                type_counts['percentage'] += 1
            elif self.patterns['currency'].match(str_val):
                type_counts['currency'] += 1
            elif self.patterns['integer'].match(str_val):
                type_counts['integer'] += 1
            elif self.patterns['decimal'].match(str_val):
                type_counts['decimal'] += 1
            elif self.patterns['date'].match(str_val):
                type_counts['date'] += 1
            elif self.patterns['boolean'].match(str_val):
                type_counts['boolean'] += 1
            else:
                type_counts['text'] += 1
        
        # Return the most common type
        return max(type_counts, key=type_counts.get)
    
    def convert_to_numeric(self, series: pd.Series, column_name: str = '') -> pd.Series:
        """Convert series to numeric, handling various formats."""
        def clean_numeric(value):
            if pd.isna(value):
                return np.nan
            
            str_val = str(value).strip()
            
            # Handle percentage
            if '%' in str_val:
                str_val = str_val.replace('%', '').strip()
                try:
                    return float(str_val) / 100
                except:
                    return np.nan
            
            # Handle currency
            str_val = re.sub(r'[$£€¥,]', '', str_val).strip()
            
            # Handle parentheses for negative numbers
            if str_val.startswith('(') and str_val.endswith(')'):
                str_val = '-' + str_val[1:-1]
            
            # Handle story points (allow .5 values)
            if column_name.lower() in ['story points', 'story_points', 'storypoints']:
                try:
                    val = float(str_val)
                    # Common story point values: 0.5, 1, 2, 3, 5, 8, 13, 21
                    if val in [0.5, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]:
                        return val
                    else:
                        # Round to nearest valid story point
                        valid_points = [0.5, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
                        return min(valid_points, key=lambda x: abs(x - val))
                except:
                    return np.nan
            
            # Try conversion
            try:
                return float(str_val)
            except:
                return np.nan
        
        return series.apply(clean_numeric)
    
    def convert_to_date(self, series: pd.Series) -> pd.Series:
        """Convert series to datetime, trying multiple formats."""
        def parse_date(value):
            if pd.isna(value):
                return pd.NaT
            
            str_val = str(value).strip()
            
            # Try each date format
            for fmt in self.date_formats:
                try:
                    return pd.to_datetime(str_val, format=fmt)
                except:
                    continue
            
            # Try pandas intelligent parsing as fallback
            try:
                return pd.to_datetime(str_val)
            except:
                return pd.NaT
        
        return series.apply(parse_date)


class RobustDataProcessor:
    """Robust data preprocessing with comprehensive error handling."""
    
    def __init__(self):
        self.type_inferencer = DataTypeInferencer()
        self.validation_report = []
        
        # Expected columns and their types
        self.expected_schema = {
            'work_items': {
                'Work Item ID': 'id',
                'Title': 'text',
                'Work Item Type': 'category',
                'State': 'category',
                'Business Value': 'numeric',
                'Story Points': 'numeric',
                'Area Path': 'text',
                'Iteration Path': 'text',
                'Created Date': 'date',
                'PI': 'numeric'
            },
            'okrs': {
                'Objective': 'text',
                'Owner': 'text',
                'Period': 'text',
                'Level': 'category',
                'Team': 'text'
            }
        }
    
    def validate_and_clean_dataframe(
        self,
        df: pd.DataFrame,
        data_type: str = 'work_items'
    ) -> pd.DataFrame:
        """Comprehensive validation and cleaning of dataframe."""
        self.validation_report = []
        
        # Create a copy to avoid modifying original
        df_clean = df.copy()
        
        # Step 1: Basic validation
        self._validate_basic_structure(df_clean, data_type)
        
        # Step 2: Column name standardization
        df_clean = self._standardize_column_names(df_clean)
        
        # Step 3: Handle missing values
        df_clean = self._handle_missing_values(df_clean, data_type)
        
        # Step 4: Type inference and conversion
        df_clean = self._fix_data_types(df_clean, data_type)
        
        # Step 5: Validate numeric ranges
        df_clean = self._validate_numeric_ranges(df_clean, data_type)
        
        # Step 6: Handle special columns
        df_clean = self._process_special_columns(df_clean, data_type)
        
        # Step 7: Remove duplicates
        df_clean = self._remove_duplicates(df_clean, data_type)
        
        # Step 8: Final validation
        self._final_validation(df_clean, data_type)
        
        return df_clean
    
    def _validate_basic_structure(self, df: pd.DataFrame, data_type: str):
        """Validate basic dataframe structure."""
        if df.empty:
            raise DataValidationError("Dataframe is empty")
        
        if df.shape[1] == 0:
            raise DataValidationError("Dataframe has no columns")
        
        self.validation_report.append({
            'check': 'basic_structure',
            'status': 'passed',
            'details': f"Shape: {df.shape}"
        })
    
    def _standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to handle variations."""
        column_mappings = {
            # Work Item variations
            'id': 'Work Item ID',
            'workitemid': 'Work Item ID',
            'work_item_id': 'Work Item ID',
            'wi_id': 'Work Item ID',
            
            # Title variations
            'name': 'Title',
            'work_item_title': 'Title',
            'summary': 'Title',
            
            # Type variations
            'type': 'Work Item Type',
            'workitemtype': 'Work Item Type',
            'work_item_type': 'Work Item Type',
            'wi_type': 'Work Item Type',
            
            # Business Value variations
            'business_value': 'Business Value',
            'businessvalue': 'Business Value',
            'bv': 'Business Value',
            'value': 'Business Value',
            'priority': 'Business Value',
            
            # Story Points variations
            'story_points': 'Story Points',
            'storypoints': 'Story Points',
            'sp': 'Story Points',
            'points': 'Story Points',
            'effort': 'Story Points',
            'size': 'Story Points',
            
            # State variations
            'status': 'State',
            'work_item_state': 'State',
            
            # Area Path variations
            'area_path': 'Area Path',
            'areapath': 'Area Path',
            'team': 'Area Path',
            'area': 'Area Path',
            
            # Description variations
            'desc': 'Description',
            'details': 'Description',
            'body': 'Description',
            'text': 'Description'
        }
        
        # Apply mappings
        new_columns = {}
        for col in df.columns:
            col_lower = col.lower().replace(' ', '').replace('_', '')
            mapped = False
            
            for key, value in column_mappings.items():
                if col_lower == key.lower().replace(' ', '').replace('_', ''):
                    new_columns[col] = value
                    mapped = True
                    break
            
            if not mapped:
                new_columns[col] = col
        
        df = df.rename(columns=new_columns)
        
        self.validation_report.append({
            'check': 'column_standardization',
            'status': 'passed',
            'details': f"Standardized {len(new_columns)} columns"
        })
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """Handle missing values intelligently."""
        missing_report = {}
        
        for col in df.columns:
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                missing_pct = (missing_count / len(df)) * 100
                missing_report[col] = f"{missing_count} ({missing_pct:.1f}%)"
                
                # Handle based on column type
                if col in ['Business Value', 'Story Points']:
                    # Use median for numeric values
                    median_val = df[col].median()
                    if pd.notna(median_val):
                        df[col].fillna(median_val, inplace=True)
                    else:
                        df[col].fillna(0, inplace=True)
                
                elif col in ['State', 'Work Item Type']:
                    # Use mode for categorical
                    mode_val = df[col].mode()
                    if len(mode_val) > 0:
                        df[col].fillna(mode_val[0], inplace=True)
                    else:
                        df[col].fillna('Unknown', inplace=True)
                
                elif col in ['Description', 'Acceptance Criteria']:
                    # Fill text with empty string
                    df[col].fillna('', inplace=True)
                
                elif col == 'Area Path':
                    df[col].fillna('Unassigned', inplace=True)
        
        if missing_report:
            self.validation_report.append({
                'check': 'missing_values',
                'status': 'warning',
                'details': missing_report
            })
        
        return df
    
    def _fix_data_types(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """Fix data types based on intelligent inference."""
        type_fixes = {}
        
        for col in df.columns:
            if col in ['Business Value', 'Story Points', 'PI', 'Original Estimate', 'Completed Work']:
                # Convert to numeric
                original_dtype = df[col].dtype
                df[col] = self.type_inferencer.convert_to_numeric(df[col], col)
                
                # Check for conversion issues
                failed_conversions = df[col].isna().sum() - df[col].isna().sum()
                if failed_conversions > 0:
                    type_fixes[col] = f"Converted {failed_conversions} values to NaN"
            
            elif col in ['Created Date', 'Closed Date', 'Start Date', 'Target Date']:
                # Convert to datetime
                df[col] = self.type_inferencer.convert_to_date(df[col])
            
            elif col == 'Work Item ID':
                # Ensure ID is string
                df[col] = df[col].astype(str)
            
            elif col in ['State', 'Work Item Type', 'Priority']:
                # Convert to category for efficiency
                df[col] = df[col].astype('category')
        
        if type_fixes:
            self.validation_report.append({
                'check': 'type_conversion',
                'status': 'info',
                'details': type_fixes
            })
        
        return df
    
    def _validate_numeric_ranges(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """Validate and fix numeric ranges."""
        range_issues = {}
        
        # Business Value should be 0-100
        if 'Business Value' in df.columns:
            bv_col = df['Business Value']
            out_of_range = ((bv_col < 0) | (bv_col > 100)).sum()
            if out_of_range > 0:
                df.loc[bv_col < 0, 'Business Value'] = 0
                df.loc[bv_col > 100, 'Business Value'] = 100
                range_issues['Business Value'] = f"Clamped {out_of_range} values to [0, 100]"
        
        # Story Points should be positive
        if 'Story Points' in df.columns:
            sp_col = df['Story Points']
            negative = (sp_col < 0).sum()
            if negative > 0:
                df.loc[sp_col < 0, 'Story Points'] = 0
                range_issues['Story Points'] = f"Set {negative} negative values to 0"
            
            # Check for unreasonable story points
            too_large = (sp_col > 100).sum()
            if too_large > 0:
                df.loc[sp_col > 100, 'Story Points'] = 100
                range_issues['Story Points'] = f"Capped {too_large} values at 100"
        
        if range_issues:
            self.validation_report.append({
                'check': 'numeric_ranges',
                'status': 'warning',
                'details': range_issues
            })
        
        return df
    
    def _process_special_columns(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """Process special columns that need custom handling."""
        # Handle Work Item Type standardization
        if 'Work Item Type' in df.columns:
            type_mapping = {
                'story': 'User Story',
                'userstory': 'User Story',
                'user story': 'User Story',
                'bug': 'Bug',
                'defect': 'Bug',
                'task': 'Task',
                'feature': 'Feature',
                'epic': 'Epic',
                'initiative': 'Epic'
            }
            
            df['Work Item Type'] = df['Work Item Type'].str.lower().map(
                lambda x: type_mapping.get(x, x.title()) if pd.notna(x) else 'Unknown'
            )
        
        # Handle State standardization
        if 'State' in df.columns:
            state_mapping = {
                'new': 'New',
                'active': 'Active',
                'inprogress': 'Active',
                'in progress': 'Active',
                'resolved': 'Resolved',
                'closed': 'Closed',
                'done': 'Closed',
                'completed': 'Closed'
            }
            
            df['State'] = df['State'].str.lower().map(
                lambda x: state_mapping.get(x, x.title()) if pd.notna(x) else 'New'
            )
        
        # Create engineered features
        if 'Business Value' in df.columns and 'Story Points' in df.columns:
            # Value per point (handle division by zero)
            df['Value_Per_Point'] = df.apply(
                lambda row: row['Business Value'] / row['Story Points'] 
                if row['Story Points'] > 0 else 0,
                axis=1
            )
            
            # Value categories
            df['Value_Category'] = pd.cut(
                df['Business Value'],
                bins=[0, 30, 70, 100],
                labels=['Low', 'Medium', 'High']
            )
            
            # Size categories
            df['Size_Category'] = pd.cut(
                df['Story Points'],
                bins=[0, 3, 8, 21, 100],
                labels=['Small', 'Medium', 'Large', 'XLarge']
            )
        
        return df
    
    def _remove_duplicates(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """Remove duplicate entries."""
        original_count = len(df)
        
        if data_type == 'work_items' and 'Work Item ID' in df.columns:
            df = df.drop_duplicates(subset=['Work Item ID'], keep='last')
        else:
            df = df.drop_duplicates()
        
        removed = original_count - len(df)
        if removed > 0:
            self.validation_report.append({
                'check': 'duplicates',
                'status': 'info',
                'details': f"Removed {removed} duplicate rows"
            })
        
        return df
    
    def _final_validation(self, df: pd.DataFrame, data_type: str):
        """Perform final validation checks."""
        issues = []
        
        # Check for required columns
        if data_type == 'work_items':
            required = ['Work Item ID', 'Title', 'Work Item Type']
            missing = [col for col in required if col not in df.columns]
            if missing:
                issues.append(f"Missing required columns: {missing}")
        
        # Check for data consistency
        if 'Parent' in df.columns and 'Work Item ID' in df.columns:
            # Check that parent IDs exist
            parent_ids = df['Parent'].dropna().unique()
            work_item_ids = df['Work Item ID'].unique()
            orphaned = set(parent_ids) - set(work_item_ids)
            if orphaned:
                issues.append(f"Found {len(orphaned)} references to non-existent parent IDs")
        
        if issues:
            self.validation_report.append({
                'check': 'final_validation',
                'status': 'warning',
                'details': issues
            })
        else:
            self.validation_report.append({
                'check': 'final_validation',
                'status': 'passed',
                'details': 'All consistency checks passed'
            })
    
    def get_validation_report(self) -> List[Dict[str, Any]]:
        """Get the validation report."""
        return self.validation_report
    
    def print_validation_report(self):
        """Print a formatted validation report."""
        print("\n" + "="*60)
        print("DATA VALIDATION REPORT")
        print("="*60)
        
        for item in self.validation_report:
            status_symbol = {
                'passed': '✅',
                'warning': '⚠️',
                'error': '❌',
                'info': 'ℹ️'
            }.get(item['status'], '•')
            
            print(f"\n{status_symbol} {item['check'].upper()}")
            if isinstance(item['details'], dict):
                for key, value in item['details'].items():
                    print(f"   - {key}: {value}")
            else:
                print(f"   {item['details']}")
        
        print("\n" + "="*60)


class FilterableDataProcessor:
    """Enhanced data processor with filtering capabilities."""
    
    def __init__(self):
        self.robust_processor = RobustDataProcessor()
    
    def process_with_filters(
        self,
        df: pd.DataFrame,
        filters: Optional[Dict[str, Any]] = None,
        engineered_features: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Process data with filtering based on engineered features."""
        # First, clean the data
        df_clean = self.robust_processor.validate_and_clean_dataframe(df)
        
        # Apply filters if provided
        if filters:
            df_clean = self._apply_filters(df_clean, filters)
        
        # Ensure engineered features are included
        if engineered_features:
            for feature in engineered_features:
                if feature not in df_clean.columns:
                    df_clean = self._create_engineered_feature(df_clean, feature)
        
        return df_clean
    
    def _apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to dataframe."""
        df_filtered = df.copy()
        
        for column, filter_value in filters.items():
            if column not in df_filtered.columns:
                logger.warning(f"Filter column '{column}' not found in dataframe")
                continue
            
            if isinstance(filter_value, dict):
                # Range filter
                if 'min' in filter_value:
                    df_filtered = df_filtered[df_filtered[column] >= filter_value['min']]
                if 'max' in filter_value:
                    df_filtered = df_filtered[df_filtered[column] <= filter_value['max']]
            elif isinstance(filter_value, list):
                # Multiple values
                df_filtered = df_filtered[df_filtered[column].isin(filter_value)]
            else:
                # Single value
                df_filtered = df_filtered[df_filtered[column] == filter_value]
        
        logger.info(f"Filtered from {len(df)} to {len(df_filtered)} rows")
        return df_filtered
    
    def _create_engineered_feature(self, df: pd.DataFrame, feature: str) -> pd.DataFrame:
        """Create engineered features on demand."""
        if feature == 'Value_Per_Point' and 'Business Value' in df.columns and 'Story Points' in df.columns:
            df['Value_Per_Point'] = df.apply(
                lambda row: row['Business Value'] / row['Story Points'] 
                if row['Story Points'] > 0 else 0,
                axis=1
            )
        
        elif feature == 'Is_High_Priority':
            df['Is_High_Priority'] = (
                (df.get('Business Value', 0) > 70) | 
                (df.get('Priority', '').isin(['Critical', 'High']))
            )
        
        elif feature == 'Days_In_State' and 'Created Date' in df.columns:
            df['Days_In_State'] = (datetime.now() - pd.to_datetime(df['Created Date'])).dt.days
        
        return df


# Export classes
__all__ = [
    'DataValidationError',
    'DataTypeInferencer', 
    'RobustDataProcessor',
    'FilterableDataProcessor'
]