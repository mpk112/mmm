"""Quick manual test of DataLoader functionality."""

from src.data_loader import DataLoader

# Test loading the actual dataset
loader = DataLoader()

try:
    df = loader.load_data('MMM dataset - Sheet1.csv')
    print("✓ Data loaded successfully!")
    print(f"✓ Shape: {df.shape}")
    print(f"✓ Columns: {list(df.columns)}")
    print(f"✓ Date range: {df.index.min()} to {df.index.max()}")
    print(f"✓ Data types:\n{df.dtypes}")
    print(f"\n✓ First few rows:\n{df.head()}")
    print(f"\n✓ Summary statistics:\n{df.describe()}")
except Exception as e:
    print(f"✗ Error: {e}")
