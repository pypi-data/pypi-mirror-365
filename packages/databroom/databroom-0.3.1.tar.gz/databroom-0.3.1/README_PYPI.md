# Databroom

A DataFrame cleaning tool with CLI, GUI, and code generation capabilities.

## Why Databroom?

**Manual pandas approach:**
```python
# 15+ lines of repetitive code
import pandas as pd
import unicodedata

df = pd.read_csv("messy_data.csv")
# Remove empty columns
df = df.loc[:, df.isnull().mean() < 0.9]
# Clean column names
df.columns = df.columns.str.lower().str.replace(' ', '_')
# Remove accents from text values
def clean_text(text):
    if pd.isna(text): return text
    return ''.join(c for c in unicodedata.normalize('NFKD', str(text)) 
                   if not unicodedata.combining(c))
for col in df.select_dtypes(include=['object']).columns:
    df[col] = df[col].apply(clean_text)
df.to_csv("clean_data.csv", index=False)
```

**Databroom approach:**
```bash
# Single command
databroom clean messy_data.csv --clean-all --output-file clean_data.csv
```

## Installation

```bash
pip install databroom
```

## Quick Start

### Command Line Interface

```bash
# Clean everything (recommended)
databroom clean data.csv --clean-all --output-file cleaned.csv

# Clean only columns
databroom clean data.csv --clean-columns --output-file cleaned.csv

# Clean with code generation
databroom clean data.csv --clean-all --output-code script.py

# Generate R code
databroom clean data.csv --clean-all --output-code script.R --lang r

# Launch interactive GUI
databroom gui
```

### Python API

```python
from databroom.core.broom import Broom

# Load and clean data
broom = Broom.from_csv('data.csv')
cleaned = broom.clean_all()  # Smart clean everything

# Or use specific operations
cleaned = broom.clean_columns().clean_rows()

# Get cleaned DataFrame
df = cleaned.get_df()
```

## Features

- **Smart Operations**: `--clean-all`, `--clean-columns`, `--clean-rows`
- **Advanced Options**: Fine-tune with `--no-snakecase`, `--empty-threshold`, etc.
- **Code Generation**: Export Python/pandas or R/tidyverse scripts
- **Interactive GUI**: Streamlit-based web interface
- **File Support**: CSV, Excel, JSON input/output

## Available Operations

| Operation | Description |
|-----------|-------------|
| `clean_all()` | Complete cleaning: columns + rows with all operations |
| `clean_columns()` | Clean column names: snake_case + remove accents + remove empty |
| `clean_rows()` | Clean row data: snake_case + remove accents + remove empty |

### Legacy operations (still supported)
- `remove_empty_cols()`, `remove_empty_rows()`
- `standardize_column_names()`, `normalize_column_names()`
- `normalize_values()`, `standardize_values()`

## CLI Parameters

```bash
# Smart Operations
--clean-all              # Clean everything
--clean-columns          # Clean column names only  
--clean-rows            # Clean row data only

# Advanced Options
--no-snakecase          # Keep original text case
--no-remove-accents-vals # Keep accents in values
--empty-threshold 0.8   # Custom missing value threshold

# Output
--output-file clean.csv # Save cleaned data
--output-code script.py # Generate reproducible code
--lang python          # Code language (python/r)
```

## Examples

### Data Science Workflow
```bash
databroom clean survey.xlsx \
  --clean-all \
  --empty-threshold 0.7 \
  --output-file clean.csv \
  --output-code analysis.py
```

### R/Tidyverse Code Generation
```bash
databroom clean data.csv \
  --clean-all \
  --output-code analysis.R \
  --lang r
```

### Batch Processing
```bash
for file in *.csv; do
  databroom clean "$file" --clean-columns --output-file "clean_$file"
done
```

## GUI Interface

Launch the interactive web interface:

```bash
databroom gui
# Opens http://localhost:8501
```

Features:
- Drag & drop file upload
- Live preview of operations
- Interactive parameter tuning
- Real-time code generation
- One-click download

## Method Chaining

```python
from databroom.core.broom import Broom

result = (Broom.from_csv('messy_data.csv')
          .clean_columns(empty_threshold=0.8)
          .clean_rows(snakecase=False)
          .get_df())
```

## Code Generation

All operations automatically generate reproducible code:

```python
# Generated Python code
import pandas as pd
from databroom.core.broom import Broom

broom_instance = Broom.from_csv("data.csv")
broom_instance = broom_instance.clean_all()
df_cleaned = broom_instance.pipeline.df
```

## License

MIT License - see LICENSE file for details.