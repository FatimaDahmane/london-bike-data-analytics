import pandas as pd
from pathlib import Path

def save_parquet(df: pd.DataFrame, output_path: str | Path) -> None:
    """Save the cleaned DataFrame into Parquet format"""
    path = Path(output_path)
    
    # Create the parent directory if it does not exist
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save the data without the index column
    df.to_parquet(path, index=False)
    print(f"Data successfully saved to: {path}")