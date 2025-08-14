# Fantasy Football Analytics - Data Exploration
# This script explores the fantasy football data and provides insights for model development.

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path.cwd().parent / "src"))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set up plotting
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

print("Setup complete!")

# Load raw data
raw_data_path = Path("../data/raw/sample_rb_data.csv")
df = pd.read_csv(raw_data_path)

print(f"Dataset shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(df.head())

# Basic statistics
print("\nDataset Overview:")
print(f"- Seasons: {df['season'].unique()}")
print(f"- Weeks per season: {df['week'].nunique()}")
print(f"- Players: {df['player_name'].nunique()}")
print(f"- Teams: {df['team'].nunique()}")

print("\nTarget Distribution:")
print(df['over_performed'].value_counts(normalize=True))

# Fantasy points distribution
plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.hist(df['fantasy_points'], bins=30, alpha=0.7)
plt.title('Fantasy Points Distribution')
plt.xlabel('Fantasy Points')
plt.ylabel('Frequency')

plt.subplot(1, 2, 2)
plt.hist(df['projection'], bins=30, alpha=0.7, color='orange')
plt.title('Projection Distribution')
plt.xlabel('Projection')
plt.ylabel('Frequency')

plt.tight_layout()
plt.show()

# Performance vs Projection
plt.figure(figsize=(10, 6))
plt.scatter(df['projection'], df['fantasy_points'], alpha=0.5)
plt.plot([df['projection'].min(), df['projection'].max()], 
         [df['projection'].min(), df['projection'].max()], 'r--', lw=2)
plt.xlabel('Projection')
plt.ylabel('Actual Fantasy Points')
plt.title('Actual vs Projected Performance')
plt.grid(True, alpha=0.3)
plt.show()

print("Data exploration complete!")
