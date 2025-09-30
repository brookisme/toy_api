"""

Table Generator Module for Toy API

Generates dummy data tables from YAML configuration with support for various
data types, verbs (UNIQUE, CHOOSE), and constants from toy_api.constants.

License: CC-BY-4.0

"""

#
# IMPORTS
#
import csv
import json
import random
import re
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

import yaml

from toy_api.constants import (
    ADMIN_ACTIVITIES,
    FIRST_NAMES,
    JOBS,
    LANGUAGES,
    LAST_NAMES,
    LOCATIONS,
    PERMISSIONS,
    POST_TAGS,
    POST_TITLES,
    THEMES
)


#
# CONSTANTS
#
CONSTANT_MAP: Dict[str, List[str]] = {
    "FIRST_NAMES": FIRST_NAMES,
    "LAST_NAMES": LAST_NAMES,
    "POST_TITLES": POST_TITLES,
    "LOCATIONS": LOCATIONS,
    "PERMISSIONS": PERMISSIONS,
    "THEMES": THEMES,
    "LANGUAGES": LANGUAGES,
    "POST_TAGS": POST_TAGS,
    "ADMIN_ACTIVITIES": ADMIN_ACTIVITIES,
    "JOBS": JOBS,
    # Singular versions
    "FIRST_NAME": FIRST_NAMES,
    "LAST_NAME": LAST_NAMES,
    "POST_TITLE": POST_TITLES,
    "LOCATION": LOCATIONS,
    "PERMISSION": PERMISSIONS,
    "THEME": THEMES,
    "LANGUAGE": LANGUAGES,
    "POST_TAG": POST_TAGS,
    "ADMIN_ACTIVITY": ADMIN_ACTIVITIES,
    "JOB": JOBS,
}


#
# PUBLIC
#
def create_table(
        table_config: Union[str, Dict[str, Any]],
        dest: Optional[str] = None,
        file_type: Literal['parquet', 'csv', 'json', 'ld-json'] = 'parquet',
        partition_cols: Optional[List[str]] = None,
        to_dataframe: bool = False) -> Union[List[Dict[str, Any]], Any]:
    """Create table data from configuration.

    Args:
        table_config: Path to YAML config file or config dictionary.
        dest: Optional destination path to write file.
        file_type: Output file format (parquet, csv, json, ld-json).
        partition_cols: Columns to partition by (parquet only).
        to_dataframe: Return DataFrame instead of list of dicts (if pandas available).

    Returns:
        List of dictionaries (one per row) or DataFrame if to_dataframe=True.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        ValueError: If config format is invalid.
    """
    # Load configuration
    if isinstance(table_config, str):
        config = _load_config(table_config)
    else:
        config = table_config

    # Parse configuration
    config_values = config.get("config", {})
    shared_def = config.get("shared", {})
    tables_def = config.get("tables", {})

    # Generate shared data
    shared_data = _generate_shared(shared_def, config_values)

    # Generate all tables
    all_tables = {}
    for table_name, columns in tables_def.items():
        table_data = _generate_table(table_name, columns, shared_data, config_values)
        all_tables[table_name] = table_data

    # Write to file if dest provided
    if dest:
        _write_tables(all_tables, dest, file_type, partition_cols)

    # Return results
    if len(all_tables) == 1:
        # Single table - return just the table data
        result = list(all_tables.values())[0]
    else:
        # Multiple tables - return dict of table_name -> data
        result = all_tables

    # Convert to dataframe if requested
    if to_dataframe:
        try:
            import pandas as pd
            if isinstance(result, list):
                return pd.DataFrame(result)
            else:
                return {name: pd.DataFrame(data) for name, data in result.items()}
        except ImportError:
            # Pandas not available, return list of dicts
            pass

    return result


#
# INTERNAL
#
def _load_config(config_path: str) -> Dict[str, Any]:
    """Load YAML configuration file.

    Args:
        config_path: Path to YAML configuration file.

    Returns:
        Configuration dictionary.

    Raises:
        FileNotFoundError: If config file doesn't exist.
    """
    with open(config_path, 'r') as file:
        return yaml.safe_load(file) or {}


def _generate_shared(shared_def: Dict[str, Any], config_values: Dict[str, Any]) -> Dict[str, List[Any]]:
    """Generate shared data columns.

    Args:
        shared_def: Shared column definitions.
        config_values: Config values for substitution.

    Returns:
        Dictionary mapping column names to lists of values.
    """
    shared_data = {}

    for col_spec, value_spec in shared_def.items():
        # Parse column name and optional row count
        col_name, row_count = _parse_column_spec(col_spec, config_values)

        # Generate column data
        column_values = _generate_column(value_spec, row_count, config_values, shared_data)

        shared_data[col_name] = column_values

    return shared_data


def _generate_table(
        table_spec: str,
        columns: Dict[str, Any],
        shared_data: Dict[str, List[Any]],
        config_values: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate a single table.

    Args:
        table_spec: Table name with optional row count (e.g., "users[10]").
        columns: Column definitions.
        shared_data: Shared data columns.
        config_values: Config values for substitution.

    Returns:
        List of row dictionaries.
    """
    # Parse table name and row count
    table_name, row_count = _parse_column_spec(table_spec, config_values)

    # Determine actual row count from columns or shared data
    if row_count is None:
        # Find row count from shared data references
        for col_spec in columns.values():
            if isinstance(col_spec, str) and col_spec.startswith("[[") and col_spec.endswith("]]"):
                shared_col_name = col_spec[2:-2]
                if shared_col_name in shared_data:
                    row_count = len(shared_data[shared_col_name])
                    break

        # If still no row count, use random
        if row_count is None:
            row_count = random.randint(10, 50)

    # Generate table data
    table_data = []
    for row_idx in range(row_count):
        row = {}
        for col_name, value_spec in columns.items():
            value = _generate_cell_value(value_spec, row_idx, config_values, shared_data)
            row[col_name] = value
        table_data.append(row)

    return table_data


def _generate_column(
        value_spec: str,
        row_count: Optional[int],
        config_values: Dict[str, Any],
        shared_data: Dict[str, List[Any]]) -> List[Any]:
    """Generate values for an entire column.

    Args:
        value_spec: Value specification string.
        row_count: Number of rows to generate.
        config_values: Config values for substitution.
        shared_data: Shared data columns.

    Returns:
        List of column values.
    """
    if row_count is None:
        row_count = random.randint(10, 50)

    column_values = []
    for row_idx in range(row_count):
        value = _generate_cell_value(value_spec, row_idx, config_values, shared_data)
        column_values.append(value)

    return column_values


def _generate_cell_value(
        value_spec: str,
        row_idx: int,
        config_values: Dict[str, Any],
        shared_data: Dict[str, List[Any]]) -> Any:
    """Generate a single cell value.

    Args:
        value_spec: Value specification string.
        row_idx: Row index for shared data lookup.
        config_values: Config values for substitution.
        shared_data: Shared data columns.

    Returns:
        Generated value.
    """
    # Handle shared data reference [[column_name]]
    if isinstance(value_spec, str) and value_spec.startswith("[[") and value_spec.endswith("]]"):
        shared_col_name = value_spec[2:-2]
        if shared_col_name in shared_data:
            shared_col = shared_data[shared_col_name]
            if row_idx < len(shared_col):
                return shared_col[row_idx]
            else:
                # Row index exceeds shared data length, choose random
                return random.choice(shared_col)
        else:
            raise ValueError(f"Shared column '{shared_col_name}' not found")

    # Handle special NAME constant
    if value_spec == "NAME":
        return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

    if value_spec == "NAMES":
        count = random.randint(1, 5)
        return [f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}" for _ in range(count)]

    # Handle UNIQUE verb
    if value_spec.startswith("UNIQUE["):
        return _generate_unique_value(value_spec, row_idx)

    # Handle CHOOSE verb
    if value_spec.startswith("CHOOSE["):
        return _generate_choose_value(value_spec)

    # Handle constants
    if value_spec in CONSTANT_MAP:
        # Check if it's plural form (return list) or singular (return single)
        if value_spec.endswith("S"):
            count = random.randint(1, len(CONSTANT_MAP[value_spec]))
            return random.sample(CONSTANT_MAP[value_spec], count)
        else:
            return random.choice(CONSTANT_MAP[value_spec])

    # Handle constants with selection [n] or [int]
    match = re.match(r'([A-Z_]+)\[([n0-9]+)\]', value_spec)
    if match:
        const_name = match.group(1)
        count_spec = match.group(2)

        if const_name in CONSTANT_MAP:
            const_list = CONSTANT_MAP[const_name]
            if count_spec == 'n':
                count = random.randint(1, len(const_list))
            else:
                count = int(count_spec)
            count = min(count, len(const_list))
            return random.sample(const_list, count)

    # Handle basic types
    if value_spec == "str":
        return _generate_random_string()
    elif value_spec == "int":
        return random.randint(0, 1000)
    elif value_spec == "float":
        return round(random.uniform(0, 1000), 2)
    elif value_spec == "bool":
        return random.choice([True, False])

    # Default: return as-is
    return value_spec


def _generate_unique_value(value_spec: str, row_idx: int) -> Any:
    """Generate unique value based on specification.

    Args:
        value_spec: UNIQUE specification (e.g., "UNIQUE[int]").
        row_idx: Row index to use for unique value.

    Returns:
        Unique value.
    """
    # Extract type from UNIQUE[type]
    match = re.match(r'UNIQUE\[([^\]]+)\]', value_spec)
    if not match:
        return row_idx

    value_type = match.group(1)

    if value_type == "int":
        return row_idx + 1000  # Offset to avoid small numbers
    elif value_type == "str":
        return f"unique_{row_idx:04d}"
    else:
        return f"{value_type}_{row_idx}"


def _generate_choose_value(value_spec: str) -> Any:
    """Generate value using CHOOSE verb.

    Args:
        value_spec: CHOOSE specification (e.g., "CHOOSE[[a,b,c]][[2]]").

    Returns:
        Chosen value(s).
    """
    # Parse CHOOSE[[items]][[count]] or CHOOSE[[items]]
    # Handle range syntax: CHOOSE[[21-89]]
    pattern = r'CHOOSE\[\[([^\]]+)\]\](?:\[\[([^\]]+)\]\])?'
    match = re.match(pattern, value_spec)

    if not match:
        return None

    items_spec = match.group(1)
    count_spec = match.group(2)

    # Parse items
    if '-' in items_spec and items_spec.replace('-', '').replace(' ', '').isdigit():
        # Range syntax: 21-89
        parts = items_spec.split('-')
        start = int(parts[0].strip())
        end = int(parts[1].strip())
        items = list(range(start, end + 1))
    else:
        # List syntax: a, b, c
        items = [item.strip() for item in items_spec.split(',')]

    # Determine count
    if count_spec is None:
        # No count specified - return single item
        return random.choice(items)
    elif count_spec == 'n':
        # Random count
        count = random.randint(1, len(items))
    elif count_spec == '1':
        # Exactly 1
        return random.choice(items)
    else:
        # Specific count
        count = int(count_spec)

    count = min(count, len(items))
    return random.sample(items, count)


def _parse_column_spec(col_spec: str, config_values: Dict[str, Any]) -> tuple:
    """Parse column specification to extract name and optional row count.

    Args:
        col_spec: Column specification (e.g., "user_id[10]" or "user_id[[NB_USERS]]").
        config_values: Config values for substitution.

    Returns:
        Tuple of (column_name, row_count or None).
    """
    # Handle [[CONFIG_VAR]] syntax
    match = re.match(r'([^\[]+)\[\[([^\]]+)\]\]', col_spec)
    if match:
        col_name = match.group(1)
        config_var = match.group(2)
        row_count = config_values.get(config_var)
        return col_name, row_count

    # Handle [int] syntax
    match = re.match(r'([^\[]+)\[(\d+)\]', col_spec)
    if match:
        col_name = match.group(1)
        row_count = int(match.group(2))
        return col_name, row_count

    # No row count specified
    return col_spec, None


def _generate_random_string(length: int = 10) -> str:
    """Generate random string.

    Args:
        length: Length of string.

    Returns:
        Random string.
    """
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def _write_tables(
        tables: Dict[str, List[Dict[str, Any]]],
        dest: str,
        file_type: str,
        partition_cols: Optional[List[str]] = None) -> None:
    """Write tables to files.

    Args:
        tables: Dictionary of table_name -> data.
        dest: Destination path.
        file_type: File format.
        partition_cols: Partition columns (parquet only).
    """
    dest_path = Path(dest)

    if len(tables) == 1:
        # Single table - write to dest directly
        table_data = list(tables.values())[0]
        _write_single_table(table_data, dest_path, file_type, partition_cols)
    else:
        # Multiple tables - create directory and write each table
        dest_path.mkdir(parents=True, exist_ok=True)
        for table_name, table_data in tables.items():
            table_file = dest_path / f"{table_name}.{file_type}"
            _write_single_table(table_data, table_file, file_type, partition_cols)


def _write_single_table(
        data: List[Dict[str, Any]],
        file_path: Path,
        file_type: str,
        partition_cols: Optional[List[str]] = None) -> None:
    """Write single table to file.

    Args:
        data: Table data as list of dicts.
        file_path: Output file path.
        file_type: File format.
        partition_cols: Partition columns (parquet only).
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if file_type == 'parquet':
        _write_parquet(data, file_path, partition_cols)
    elif file_type == 'csv':
        _write_csv(data, file_path)
    elif file_type == 'json':
        _write_json(data, file_path)
    elif file_type == 'ld-json':
        _write_ld_json(data, file_path)


def _write_parquet(
        data: List[Dict[str, Any]],
        file_path: Path,
        partition_cols: Optional[List[str]] = None) -> None:
    """Write data to Parquet file.

    Args:
        data: Table data.
        file_path: Output file path.
        partition_cols: Partition columns.
    """
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq

        # Convert to PyArrow table
        table = pa.Table.from_pylist(data)

        # Write with or without partitioning
        if partition_cols:
            pq.write_to_dataset(table, root_path=str(file_path.parent),
                                partition_cols=partition_cols)
        else:
            pq.write_table(table, str(file_path))
    except ImportError:
        raise ImportError("PyArrow required for Parquet support. Install with: pip install pyarrow")


def _write_csv(data: List[Dict[str, Any]], file_path: Path) -> None:
    """Write data to CSV file.

    Args:
        data: Table data.
        file_path: Output file path.
    """
    if not data:
        return

    with open(file_path, 'w', newline='') as csvfile:
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def _write_json(data: List[Dict[str, Any]], file_path: Path) -> None:
    """Write data to JSON file.

    Args:
        data: Table data.
        file_path: Output file path.
    """
    with open(file_path, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=2)


def _write_ld_json(data: List[Dict[str, Any]], file_path: Path) -> None:
    """Write data to line-delimited JSON file.

    Args:
        data: Table data.
        file_path: Output file path.
    """
    with open(file_path, 'w') as jsonfile:
        for row in data:
            jsonfile.write(json.dumps(row) + '\n')