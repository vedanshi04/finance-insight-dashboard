import pandas as pd
import warnings
import re

# Suppress specific datetime parsing warnings globally
warnings.filterwarnings("ignore", message="Could not infer format.*")

# Datetime parser(converting common_formats into datetime datatype) 
def safe_parse_datetime_column(series):
    sample = series.dropna().astype(str)
    if sample.empty:
        return pd.Series([pd.NaT] * len(series), index=series.index)

    common_formats = [
        "%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y",
        "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d",
        "%Y-%m", "%Y/%m",
        "%b %Y", "%B %Y",
        "%d %b %Y", "%d %B %Y",
        "%Y-%m-%d %H:%M:%S", "%m/%d/%Y %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y",
    ]

    for fmt in common_formats:
        try:
            parsed = pd.to_datetime(series, format=fmt, errors="coerce")
            if parsed.notna().mean() > 0.7:
                return parsed
        except Exception:
            continue

    return pd.to_datetime(series, errors="coerce")


# If column contains such mentioned phrases with numbers then do not convert it into numeric, make them categorical
# Eg. more than 5 years, 2-4 weeks - such phrases will get converted to numeric bcz of convert_erroneous_numeric_columns() function so to keep them as categorical this func is made
def contains_duration_like_phrases(text_series):
    # Combine sample into one string
    sample_text = text_series.dropna().astype(str).str.lower().head(20).str.cat(sep=' ')
    
    # Duration-related pattern: look for numbers + time units, ranges, or vague phrases
    duration_patterns = [
        r"\b\d+\s*-\s*\d+\s*(year|month)s?\b",  # e.g. 1-3 years
        r"\b(more|less)\s+than\s+\d+",          # more than 5, less than 2
        r"\b\d+\s*(year|month)s?\b",            # 2 years, 6 months
        r"\b\d+\s*to\s*\d+\b",                  # 1 to 3
        r"\byear\b", r"\bmonth\b",              # loose match fallback
    ]
    
    return any(re.search(pat, sample_text) for pat in duration_patterns)




# Main Preprocessing Function 
def preprocess(file, remove_outliers=True):
    
    if file.name.endswith(".csv"):
        try:
            df = pd.read_csv(file)
            if df.empty:
                raise ValueError("The uploaded CSV file is empty.")
        except pd.errors.EmptyDataError:
            raise ValueError("The uploaded CSV file contains no data.")
        
    elif file.name.endswith((".xlsx", ".xlsm", ".xls")):
        try:
            df = pd.read_excel(file, engine='openpyxl')
        except ImportError as e:
            raise ImportError("Install 'openpyxl' to handle Excel files.") from e
        
    else:
        raise ValueError("Unsupported file format. Please upload a .csv or .xlsx file.")

    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    original_df = df.copy()

    logs = {}

    # Drop fully empty cols and those with >= 50% missing
    before_cols = set(df.columns)
    
    df = df.dropna(axis=1, how="all")
    
    df = df.dropna(thresh=len(df) * 0.5, axis=1)
    
    after_cols = set(df.columns)
    
    dropped_cols = before_cols - after_cols
    logs["dropped_columns"] = list(dropped_cols)


    # Try parsing object columns as datetime (safely)
    for col in df.columns:
        if df[col].dtype == 'object':
            parsed = safe_parse_datetime_column(df[col])
            if parsed.notna().mean() > 0.7:
                df[col] = parsed


    # Drop duplicates
    before_dup = len(df)
    df = df.drop_duplicates()
    logs["duplicates_removed"] = before_dup - len(df)


    # Handle mostly-numeric object columns
    df = convert_erroneous_numeric_columns(df, threshold=0.7)


    # Detect column types + update df
    column_types, df = detect_column_types(df)


    # Fill NaNs
    df = fill_nan_cells(df, column_types)


    # Remove outliers
    if remove_outliers:
        df, outliers_removed = remove_outliers_iqr(df, column_types)
        logs["outliers_removed"] = outliers_removed
    else:
        logs["outliers_removed"] = 0

    return original_df, df, column_types, logs



# Detect Column Types 
def detect_column_types(df):
    cleaned_df = df.copy()
    column_types = {}

    for col in df.columns:
        series = df[col]

        # Check for actual datetime dtype
        if pd.api.types.is_datetime64_any_dtype(series):
            column_types[col] = "datetime"
            continue

        # Try parsing datetime strings
        if series.dtype == 'object':
            parsed = safe_parse_datetime_column(series)
            if parsed.notna().mean() >= 0.7:
                cleaned_df[col] = parsed
                column_types[col] = "datetime"
                continue

        # Detect boolean-like object columns, but keep original values
        if series.dtype == 'object':
            lower_series = series.astype(str).str.strip().str.lower()
            unique_vals = set(lower_series.dropna().unique())
            boolean_values = {"true", "false", "yes", "no", "1", "0"}

            if unique_vals.issubset(boolean_values):
                column_types[col] = "boolean"
                continue

        # Detect numeric-like object columns
        if series.dtype == 'object':
            if contains_duration_like_phrases(series):
                column_types[col] = "categorical"
                continue  # Don't try to make this numeric
            
            # Such works will be converted & treated as NaN
            cleaned = series.astype(str).str.strip()
            cleaned = cleaned.replace(['$', '$-', '-', 'None', 'none', 'nan', 'NaN', ''], pd.NA)
            cleaned = cleaned.str.replace(r'[^\d\.\-%]', '', regex=True)
            is_percent = cleaned.str.contains('%')
            cleaned = cleaned.str.replace('%', '', regex=False)

            # Convert to numeric wherever possible
            numeric_series = pd.to_numeric(cleaned, errors='coerce')
            if is_percent.any():
                numeric_series[is_percent] = numeric_series[is_percent] / 100.0

            if numeric_series.notna().sum() > 0:
                cleaned_df[col] = numeric_series
                column_types[col] = "numeric"
                continue

        if pd.api.types.is_bool_dtype(series):
            column_types[col] = "boolean"
            continue

        if pd.api.types.is_numeric_dtype(series):
            column_types[col] = "numeric"
            continue

        if series.dtype == 'object' or series.dtype.name == 'category':
            nunique = series.nunique(dropna=True)
            if nunique < 0.5 * len(series):
                column_types[col] = "categorical"
            else:
                column_types[col] = "text"
            continue

        column_types[col] = "non-numeric"

    return column_types, cleaned_df



# Fill Missing Values
def fill_nan_cells(df, column_types):
    df = df.copy()
    for col, col_type in column_types.items():
        if df[col].isnull().sum() == 0:
            continue
        
        # if datetime then ffill
        if col_type == "datetime":
            df[col] = df[col].ffill()
 
        # if numeric - if skew then fill with median and if normal col then fill with mean
        elif col_type == "numeric":
            skew_val = df[col].skew()
            if skew_val > 1 or skew_val < -1:
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna(df[col].mean())

        # if categorical or boolean fill with mode if it exists
        elif col_type in ["categorical", "boolean"]:
            mode_val = df[col].mode()
            if not mode_val.empty:
                df[col] = df[col].fillna(mode_val[0])
    return df


# If some column exists that is majorly numeric but has some ambiguities then convert those erroneous values to NaN
# Handle Mostly-Numeric Object Columns 
def convert_erroneous_numeric_columns(df, threshold=0.7):
    df_cleaned = df.copy()

    for col in df.columns:
        if df[col].dtype == 'object':
            parsed = safe_parse_datetime_column(df[col])
            if parsed.notna().mean() > 0.7:
                continue
            
            if contains_duration_like_phrases(df[col]):
                continue
            
            
            coerced = pd.to_numeric(df[col], errors='coerce')
            numeric_fraction = coerced.notna().mean()

            if numeric_fraction >= threshold:
                df_cleaned[col] = coerced

    return df_cleaned


# Remove Outliers Using IQR
def remove_outliers_iqr(df, column_types):
    df_out = df.copy()
    original_rows = len(df_out)

    for col, col_type in column_types.items():
        if col_type == "numeric":
            Q1 = df_out[col].quantile(0.25)
            Q3 = df_out[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            mask = (df_out[col] >= lower) & (df_out[col] <= upper)
            mask = mask.fillna(False)
            df_out = df_out[mask]

    rows_removed = original_rows - len(df_out)
    return df_out, rows_removed